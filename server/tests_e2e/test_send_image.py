import pytest
import requests
from PIL import Image
from io import BytesIO
from base64 import b64encode

endpoint = "http://localhost:8000/faces"


def test_upload_image():
    # TODO - test with real data / raw TCP socket

    image_bytes = BytesIO()
    Image.open('./stock_photo.jpg').save(image_bytes, format='jpeg')
    image_bytes.seek(0)  # reset cursor

    # print(image_bytes.read())

    images = [b64encode(image_bytes.read()).decode('utf-8')]

    body = {"images": images}

    r = requests.request("POST", url=endpoint, json=body)
    print(f"Response: {r.text}")
    r.raise_for_status()
