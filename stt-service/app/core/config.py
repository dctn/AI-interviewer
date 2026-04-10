import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_STT_MODEL = os.getenv("GROQ_STT_MODEL", "whisper-large-v3").strip()

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")