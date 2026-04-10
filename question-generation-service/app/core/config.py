import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192").strip()

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")