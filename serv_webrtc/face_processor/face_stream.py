import cv2
import numpy as np
import queue
import asyncio
import time
import findfaces

import face_recognition

from findfaces import FaceBox
from aiortc import VideoStreamTrack
from av import VideoFrame
from loguru import logger as log

from database.database import SessionLocal, engine
from database import models, crud

# Initialize database
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Global frame variable to pass between threads
current_face = None  # start w/ an empty frame
latest_frame = False
frame_lock = False  # mutex-lock. More efficient than doing a deep-copy

known_faces = crud.get_all_users(db)
log.info(f'Loaded {len(known_faces)} profiles from database!')


class FaceStreamTrack(VideoStreamTrack):
    """
    A video track that returns an animated flag.
    """

    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track
        self.last_frame = None
        self.frame_counter = 0
        self.update_frames = 120

        # Start our worker thread        
        self.worker = asyncio.create_task(self._face_analyzer_thread())
        
    async def recv(self):

        self.frame_counter += 1
        # Grab the frame
        frame = await self.track.recv()

        # If it's been x frames since our last update
        if self.frame_counter >= self.update_frames \
                and not frame_lock:

            # Assign it to our global variable            
            global latest_frame
            latest_frame = frame.to_ndarray()

            # Reset frame counter
            self.frame_counter = 0

        # Return whatever we have queued up
        if current_face is not None:
            new_frame = VideoFrame.from_ndarray(current_face, format="yuv420p")
        else:
            new_frame = VideoFrame(300, 300, format="yuv420p")

        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

    async def _face_analyzer_thread(self):
        """
        Separate worker thread to analyze last images seen
        """
        
        log.debug("Starting face worker thread")
        
        def reset_processed_frame():
            """
            Helper function to clear our latest_frame and update lock
            """
    
            # Blank frame
            global latest_frame
            latest_frame = None

            # Disable lock            
            global frame_lock
            frame_lock = False
            
            log.debug('Frame lock: enabled!')
            
        def get_process_frame():
            """
            Helper function to get frame and enable lock if frame is not none
            """
            global latest_frame
            global frame_lock
            if latest_frame is not None and not frame_lock:
                # Enable lock
                frame_lock = True
                
                log.debug('Frame lock: disabled!')
        
            # Return latest frame (can be None)
            return latest_frame

        while True:
            
            img = get_process_frame()
            # If we don't have any frames to analyze, sleep+reset
            if img is None:
                await asyncio.sleep(.1)
                continue

            # Find faces
            faces = findfaces.get_face_locations(img)
            log.info(f'Found {len(faces)} faces!')

            # TODO - implement find largest face pattern

            if len(faces) == 0:
                log.info('No faces found in last frame....')
                reset_processed_frame()
                continue
            face = faces[0]

            # Get face encoding
            # This is just how locations need to be formatted for this function
            locs = (face.top_y, face.bottom_x, face.bottom_y, face.top_x)
            encodings = face_recognition.face_encodings(img, locs)
            if len(encodings) == 0:
                log.error(f'Face found but unable to get encoding!')
                reset_processed_frame()
                continue
            # Grab the first/only encoding
            encoding = encodings[0]

            # Get our closest match
            match, score = self._find_closest_face_match(known_faces, encoding)
            log.debug(f'Match found: {match} ({score})')

            # Figure our alhosn status
            alhosn_status = crud.get_alhosn_status(db, closest_match)
            log.debug(f'Profile alhosn: {alhosn_status}')
            color = (0, 0, 255)  # default red
            if alhosn_status == "green":
                color = (0, 255, 0)
            elif alhosn_status == "gray":
                color = (100, 100, 100)

            # Image manipulation
            img = self._crop_face_from_image(img, face)
            img = self._scale_image_to_height(img, desired_height=300)
            img = self._draw_inner_rectangle(img, rgb=color)

            # Update our global var
            global current_face
            current_face = img

            # Reset mutex
            reset_processed_frame()

    @staticmethod
    def _crop_face_from_image(img, face: FaceBox, buffer_percent=10) -> np.ndarray:
        """
        Crops an image around a face.
        Adds a small buffer relative to the face size.
        """

        # Set aliases from our class
        x1 = face.top_x
        x2 = face.bottom_x
        y1 = face.top_y
        y2 = face.bottom_y

        # Create a buffer that's 10% of face height
        buffer_amount = int(buffer_percent/100 * (y2 - y1))
        x1 -= buffer_amount
        x2 += buffer_amount
        y1 -= buffer_amount
        y2 += buffer_amount

        # Slice our array
        return img[x1:x2, y1:y2]

    @staticmethod
    def _scale_image_to_height(img, desired_height: int) -> np.ndarray:
        """
        Scales an image down to a desired height.
        This function makes sure to maintain the image
        aspect ratio.
        """

        # Get image dims
        height, width, _ = img.shape

        # Calculate what our scale factor should be
        scale_factor = desired_height / height

        # Calculate new image dimensions
        # new_dims = int(width * scale_factor), int(height * scale_factor)
        new_dims = 300, 300

        # Do the actual resize operation
        img = cv2.resize(img, new_dims, interpolation=cv2.INTER_AREA)

        return img

    @staticmethod
    def _draw_inner_rectangle(img, buffer_percent=10, rgb=(0, 255, 0), weight=5) -> np.ndarray:
        """
        Draws a rectangle inside an image.
        Will indent buffer_percent according to both
        the height and the width values.
        """

        # Get image dims
        height, width, _ = img.shape

        # Calculate buffer amounts
        rectangle_buffer_x = int(height * (buffer_percent/100))
        rectangle_buffer_y = int(width * (buffer_percent/100))

        # Bottom left is at 0+buffer:
        rec_x1 = rectangle_buffer_x
        rec_y1 = rectangle_buffer_y

        # Top right is at width-buffer:
        rec_x2 = width - rectangle_buffer_x
        rec_y2 = height - rectangle_buffer_y

        # Draw the actual rectangle
        cv2.rectangle(img, (rec_y1, rec_x1), (rec_y2, rec_x2), rgb, weight)

        return img

    @staticmethod
    def _cosine_similarity(f1: np.ndarray, f2: np.ndarray) -> float:
        """
        Find cos(theta) between two angles.

        1 = Perfect match
        0 = Complete opposite

        cos(theta) = 1 means theta=0. If our angle is 0,
        it's the same point.

        Higher values = closer matches
        Lower values = further matches
        """

        # Calculate the dot product of our values
        dot_product = sum(v1 * v2 for v1, v2 in zip(f1[0], f2[0]))

        # Calculate Frobenius norms
        f1_norm = sum([x ** 2 for x in f1[0]]) ** (1 / 2)
        f2_norm = sum([x ** 2 for x in f2[0]]) ** (1 / 2)

        # This is cos(theta):
        cos_theta = dot_product / (f1_norm * f2_norm)

        return cos_theta

    @staticmethod
    def _find_closest_face_match(profiles: list, f1: np.ndarray):
        dists = np.array([FaceStreamTrack._cosine_similarity(profile, f1) for profile in profiles.values()])

        closest_match = np.argmax(dists)
        profile_name = list(profiles)[closest_match]
        score = round(100 * dists[closest_match], 2)

        return profile_name, score
