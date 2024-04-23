from pydantic import BaseModel, Base64Str


class DetectionTaskError(BaseModel):
    error: bool
    message: str


class DetectionTaskRequest(BaseModel):
    task: int
    base64_img: Base64Str


class DetectionTaskResponse(BaseModel):
    success: bool
    error: DetectionTaskError
