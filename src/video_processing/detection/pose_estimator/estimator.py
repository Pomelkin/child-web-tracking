import numpy as np
from typing import Optional
import ultralytics
from src.config import settings
from ultralytics import YOLO


class PoseEstimator:
    def __init__(self) -> None:
        self.pose_estimator = YOLO(
            settings.paths_to_models.pose_estimation_model_dir, verbose=True
        )

    def detect_keypoints(
        self, frame: np.ndarray, verbose: Optional[bool] = False
    ) -> list:
        return self.pose_estimator.predict(source=frame, verbose=verbose)
