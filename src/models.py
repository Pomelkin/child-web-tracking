from pydantic import BaseModel, Base64Str


class Stream(BaseModel):
    b64_frame: str
