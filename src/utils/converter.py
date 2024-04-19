import base64
from multiprocessing.connection import Connection
import cv2
import numpy as np


def img_converter(connection: Connection) -> None:
    while True:
        try:
            data = connection.recv()
            base64_img = data
            bytes_img = base64.b64decode(base64_img)
            arr_img = np.frombuffer(bytes_img, dtype=np.uint8)
            img = cv2.imdecode(arr_img, cv2.IMREAD_COLOR)
            connection.send(img)
        except EOFError:
            break
    return
