import numpy as np
from ultralytics import YOLO
from src.config import settings


class HandDetector:
    def __init__(self) -> None:
        self._hand_detector = YOLO(settings.model_paths.hand_detector_model_dir)

    def detect_hands(self, frame: np.ndarray, verbose: bool = False) -> list:
        return self._hand_detector.predict(source=frame, verbose=verbose)
