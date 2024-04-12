import numpy as np
from typing import Optional
from src.config import settings
from ultralytics import YOLO


class PoseEstimator:
    def __init__(self) -> None:
        self._pose_estimator = YOLO(
            settings.model_paths.pose_estimation_model_dir, verbose=True
        )

    def detect_keypoints(
        self, frame: np.ndarray, verbose: Optional[bool] = False
    ) -> list:
        return self._pose_estimator.predict(source=frame, verbose=verbose)
