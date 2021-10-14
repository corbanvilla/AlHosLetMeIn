from fastapi import FastAPI, HTTPException
from typing import List
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
        # Load our image into a bytes stream
        decoded_image_stream = BytesIO(b64decode(face.image))

        # Attempt to open and convert to RGB
        image = Image.open(decoded_image_stream).convert('RGB')  # TODO - swap with jpeg lib
        image.save('recieved_photo.jpg')

        print("saved image")

        # print(f'Image of len: {len(decoded_image_stream)} received!')
    except Exception as e:
        print(f'Unable to decode image: {e}')
        raise HTTPException(status_code=500, detail="Unable to process image!")

    return 200

