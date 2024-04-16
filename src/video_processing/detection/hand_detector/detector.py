import numpy as np
from ultralytics import YOLO
from src.config import settings


class HandDetector:
    def __init__(self) -> None:
        self.hand_detector = YOLO(settings.paths_to_models.hand_detector_model_dir)

    def detect_hands(self, frame: np.ndarray, verbose: bool = False) -> list:
        return self.hand_detector.predict(source=frame, verbose=verbose)
