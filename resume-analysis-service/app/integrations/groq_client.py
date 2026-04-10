import requests
from app.core.config import GROQ_API_KEY, GROQ_MODEL

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def analyze_resume_with_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert resume parser that returns only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=90
    )

    if response.status_code != 200:
        raise Exception(f"Groq API Error {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def fix_resume_json_with_groq(raw_output: str) -> str:
    fix_prompt = f"""
Convert the following text into valid JSON only.
Do not include markdown.
Do not include explanation.

Text:
{raw_output}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a JSON repair assistant. Return only valid JSON."
            },
            {
                "role": "user",
                "content": fix_prompt
            }
        ],
        "temperature": 0
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=90
    )

    if response.status_code != 200:
        raise Exception(f"Groq JSON Fix Error {response.status_code}: {response.text}")

    data 