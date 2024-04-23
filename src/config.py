from pydantic_settings import BaseSettings, SettingsConfigDict
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
        BASE_DIR / "nn_models" / "body" / "yolov8m-pose.pt"
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
    paths_to_models: ModelPaths = ModelPaths()


settings = Settings()
