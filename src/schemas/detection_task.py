from pydantic import BaseModel, Base64Str


class DetectionTaskRequest(BaseModel):
    task: str
    base64_img: Base64Str


class DetectionTaskResponse(BaseModel):
    too_many_persons: bool
    success: bool
