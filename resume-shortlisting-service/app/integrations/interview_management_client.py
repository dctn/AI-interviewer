import requests
from app.core.config import INTERVIEW_MANAGEMENT_API_URL


def call_auto_schedule(candidate_name: str, email: str, role: str):
    payload = {
        "candidate_name": candidate_name,
        "email": email,
        "role": role,
        "interview_date": "auto",
        "interview_time": "auto",
        "status": "scheduled"
    }

    response = requests.post(
        INTERVIEW_MANAGEMENT_API_URL,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"Interview Management API Error {response.status_code}: {response.text}")

    return response.json()