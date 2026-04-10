from pydantic import BaseModel


class STTResponse(BaseModel):
    message: str
    transcript: str
    file_name: str