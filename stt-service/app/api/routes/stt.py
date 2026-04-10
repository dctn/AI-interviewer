import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.stt import STTResponse
from app.integrations.groq_stt_client import transcribe_audio_with_groq

router = APIRouter(tags=["STT"])

UPLOAD_DIR = "audio_inputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/transcribe-audio", response_model=STTResponse)
def transcribe_audio(file: UploadFile = File(...)):
    try:
        original_name = file.filename
        extension = os.path.splitext(original_name)[1].lower()

        if extension not in [".wav", ".mp3", ".m4a", ".ogg", ".webm"]:
            raise HTTPException(
                status_code=400,
                detail="Only wav, mp3, m4a, ogg, webm audio files are allowed"
            )

        safe_file_name = f"{uuid.uuid4().hex}_{original_name}"
        file_path = os.path.join(UPLOAD_DIR, safe_file_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcript = transcribe_audio_with_groq(file_path, safe_file_name)

        return STTResponse(
            message="Audio transcribed successfully",
            transcript=transcript,
            file_name=safe_file_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))