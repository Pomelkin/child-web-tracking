from pydantic_settings import BaseSettings
from pydantic import FilePath, BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent


class ModelPaths(BaseModel):
    gesture_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "hands" / "gesture_recognizer.task"
    )
    hand_detector_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "hands" / "yolov8m-hand_detector.pt"
    )
    pose_estimation_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "body" / "yolov8m-pose.pt"
    )


class Settings(BaseSettings):
    model_paths: ModelPaths = ModelPaths()


settings = Settings()
