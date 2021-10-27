import pytest
import requests
from PIL import Image
from io import BytesIO
from base64 import b64encode


def test_upload_image():
    # TODO - test with real data / raw TCP socket

    endpoint = "http://10.7.0.3:80/faces"

    image_bytes = BytesIO()
    Image.open('/Users/animcogn/Downloads/corban villa.jpg').save(image_bytes, format='jpeg')
    image_bytes.seek(0)  # reset cursor

    # print(image_bytes.read())

    images = b64encode(image_bytes.read()).decode('utf-8')

    body = {"image": images}

    r = requests.request("POST", url=endpoint, json=body)
    print(f"Response: {r.text}")
    r.raise_for_status()


def test_save_face_encoding():

    # image_name, user_id = ("corban villa.jpg", 1)
    image_name, user_id = ("IMG_3420.jpg", 2)  # aren

    endpoint = f"http://10.7.0.3:80/save_face_encoding?user_id={user_id}"

    image_bytes = BytesIO()
    Image.open(f'/Users/animcogn/Downloads/{image_name}').save(image_bytes, format='jpeg')
    image_bytes.seek(0)  # reset cursor

    # print(image_bytes.read())

    images = b64encode(image_bytes.read()).decode('utf-8')

    body = {"image": images}

    r = requests.request("POST", url=endpoint, json=body)
    print(f"Response: {r.text}")
    r.raise_for_status()

