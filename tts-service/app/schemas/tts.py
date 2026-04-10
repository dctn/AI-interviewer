from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    file_name: str = "question_audio"


class TTSResponse(BaseModel):
    message: str
    audio_url: str
    file_name: str