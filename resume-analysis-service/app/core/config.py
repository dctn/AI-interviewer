import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Resume Analysis Service")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192").strip()
QUESTION_GENERATION_API_URL = os.getenv(
    "QUESTION_GENERATION_API_URL",
    "http://127.0.0.1:8000/generate-questions"
)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")