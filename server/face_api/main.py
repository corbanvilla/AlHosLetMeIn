import time
import pickle


from loguru import logger as log

from io import BytesIO
from base64 import b64decode

import face_recognition

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from face_api.database.database import SessionLocal, engine
from face_api.database import models, crud
from face_api.recognition import find_closest_match

# Initialize database
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
app = FastAPI()

profiles = crud.get_all_users(db)
log.infog(f'Loaded {len(profiles)} profiles from database!')


class ImageUpload(BaseModel):
    image: str


@app.post("/faces")
def find_faces(face: ImageUpload):

    try:
        start = time.time()

        # Load our image into a bytes stream
        decoded_image_stream = BytesIO(b64decode(face.image))

        # Attempt to open and convert to RGB
        image = face_recognition.load_image_file(decoded_image_stream)  # TODO - swap with jpeg lib
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # Run recognition
        for face in face_encodings:
            closest_match, match_score = find_closest_match(profiles, face)
            print(f"Match found: {closest_match} ({match_score})")

        elapsed = time.time()-start
        print(f"Found faces: {len(face_locations)} in {elapsed} time.")

    except Exception as e:
        print(f'Unable to decode image: {e}')
        raise HTTPException(status_code=500, detail="Unable to process image!")

    return 200


@app.post("/save_face_encoding")
def save_face_encodings(user_id: int, face: ImageUpload):

    try:
        # Load our image into a bytes stream
        decoded_image_stream = BytesIO(b64decode(face.image))

        # Attempt to open and convert to RGB
        image = face_recognition.load_image_file(decoded_image_stream)  # TODO - swap with jpeg lib
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # Save our first encoding found in the list
        crud.set_face_encoding(db, user_id, pickle.dumps(face_encodings[0]))

    except Exception as e:
        print(f'Unable to decode image: {e}')
        raise HTTPException(status_code=500, detail="Unable to process image!")

    return 200
