import requests
from app.core.config import GROQ_API_KEY, GROQ_MODEL

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_questions_from_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def fix_json_with_groq(raw_output: str) -> str:
    fix_prompt = f"""
You are a JSON repair assistant.

Convert the following text into valid JSON only.
Do not add explanation.
Do not add markdown.

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
            {"role": "user", "content": fix_prompt}
        ],
        "temperature": 0
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]