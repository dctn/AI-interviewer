import requests
from app.core.config import GROQ_API_KEY, GROQ_STT_MODEL


def transcribe_audio_with_groq(file_path: str, file_name: str) -> str:
    """
    Groq-style audio transcription call.
    This assumes Groq supports an OpenAI-compatible audio transcription endpoint.
    If Groq account/model does not support it, API will fail and error text will reveal the exact issue.
    """

    url = "https://api.groq.com/openai/v1/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    with open(file_path, "rb") as audio_file:
        files = {
            "file": (file_name, audio_file)
        }

        data = {
            "model": GROQ_STT_MODEL
        }

        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )

    if response.status_code != 200:
        raise Exception(f"Groq STT API Error {response.status_code}: {response.text}")

    result = response.json()

    # OpenAI-compatible audio transcription APIs usually return {"text": "..."}
    transcript = result.get("text", "")
    if not transcript:
        raise Exception(f"No transcript text found in Groq response: {result}")

    return transcript