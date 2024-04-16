import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.gesture_recognizer import GestureRecognizerResult
import cv2
from src.config import settings


class GestureRecognizer:
    def __init__(self) -> None:
        base_options = python.BaseOptions(
            model_asset_path=settings.paths_to_models.gesture_model_dir
        )
        options = vision.GestureRecognizerOptions(
            base_options=base_options, num_hands=2
        )
        self._recognizer = vision.GestureRecognizer.create_from_options(options)
        return

    def recognize_gesture(self, image: np.ndarray) -> GestureRecognizerResult:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        return self._recognizer.recognize(mp_image)
