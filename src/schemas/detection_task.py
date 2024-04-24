from pydantic import BaseModel


class DetectionTaskError(BaseModel):
    error: bool
    message: str


class DetectionTaskRequest(BaseModel):
    task: int
    base64_img: str


class DetectionTaskResponse(BaseModel):
    non_processed: bool = False
    success: bool
    error: DetectionTaskError
