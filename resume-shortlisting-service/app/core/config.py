import os
from dotenv import load_dotenv

load_dotenv()

INTERVIEW_MANAGEMENT_API_URL = os.getenv(
    "INTERVIEW_MANAGEMENT_API_URL",
    "http://127.0.0.1:8004/auto-schedule"
)

SHORTLIST_THRESHOLD = int(os.getenv("SHORTLIST_THRESHOLD", "40"))