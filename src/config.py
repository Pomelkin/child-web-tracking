from pydantic_settings import BaseSettings
from pydantic import FilePath, BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent


# TODO: read type and version of models from .env
class ModelPaths(BaseModel):
    gesture_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "hands" / "gesture_recognizer.task"
    )
    hand_detector_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "hands" / "yolov8m-hand_detector.pt"
    )
    pose_estimation_model_dir: FilePath = (
        BASE_DIR / "nn_models" / "body" / "yolov8n-pose.pt"
    )


class Settings(BaseSettings):
    paths_to_models: ModelPaths = ModelPaths()
    num_workers: int


settings = Settings()
