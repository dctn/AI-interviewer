from groq import Groq
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def transcribe_audio_with_groq(file_path, file_name):
    with open(file_path, 'rb') as f:
        transcription = client.audio.transcriptions.create(
            file=(file_name, f, 'audio/webm'),
            model="whisper-large-v3-turbo"
        )
    return transcription.text
