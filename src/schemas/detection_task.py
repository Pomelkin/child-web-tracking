from pydantic import BaseModel, Base64Str


class DetectionTaskError(BaseModel):
    error: bool
    message: str


class DetectionTaskRequest(BaseModel):
    task: str
    base64_img: Base64Str


class DetectionTaskResponse(BaseModel):
    success: bool
    error: DetectionTaskError
