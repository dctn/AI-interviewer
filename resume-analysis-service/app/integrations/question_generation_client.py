import requests
from app.core.config import QUESTION_GENERATION_API_URL


def call_question_generation_service(
    role: str,
    job_description: str,
    resume_text: str,
    question_count: int,
    difficulty: str
):
    payload = {
        "role": role,
        "job_description": job_description,
        "resume_text": resume_text,
        "question_count": question_count,
        "difficulty": difficulty
    }

    response = requests.post(
        QUESTION_GENERATION_API_URL,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"Question Generation API Error {response.status_code}: {response.text}")

    return response.json()