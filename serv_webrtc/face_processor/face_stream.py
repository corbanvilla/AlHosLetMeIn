import cv2
import numpy

from aiortc import VideoStreamTrack


class FaceStreamTrack(VideoStreamTrack):
    """
    A video track that returns an animated flag.
    """

    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track

    async def recv(self):

        log.debug("Recieved frame")
        frame = await self.track.recv()

        return frame
