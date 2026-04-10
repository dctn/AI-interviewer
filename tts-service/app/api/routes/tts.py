import os
import uuid
from gtts import gTTS
from fastapi import APIRouter, HTTPException, Request
from app.schemas.tts import TTSRequest, TTSResponse

router = APIRouter(tags=["TTS"])

AUDIO_DIR = "audio_outputs"
os.makedirs(AUDIO_DIR, exist_ok=True)


@router.post("/generate-audio", response_model=TTSResponse)
async def generate_audio(payload: TTSRequest, request: Request):
    try:
        safe_file_name = f"{payload.file_name}_{uuid.uuid4().hex[:8]}.mp3"
        output_path = os.path.join(AUDIO_DIR, safe_file_name)

        tts = gTTS(text=payload.text, lang="en")
        tts.save(output_path)

        base_url = str(request.base_url).rstrip("/")
        audio_url = f"{base_url}/audio/{safe_file_name}"

        return TTSResponse(
            message="Audio generated successfully",
            audio_url=audio_url,
            file_name=safe_file_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))