import base64
import cv2
import numpy as np


def img_converter(base64_img: str) -> np.ndarray:
    bytes_img = base64.b64decode(base64_img)
    arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
    img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)
    return img
