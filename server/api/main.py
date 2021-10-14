import time

import face_recognition

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from base64 import b64decode
from PIL import Image
from io import BytesIO


app = FastAPI()


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
        faces = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
        elapsed = time.time()-start
        print(f"Found faces: {len(faces)} in {elapsed} time.")

    except Exception as e:
        print(f'Unable to decode image: {e}')
        raise HTTPException(status_code=500, detail="Unable to process image!")

    return 200
