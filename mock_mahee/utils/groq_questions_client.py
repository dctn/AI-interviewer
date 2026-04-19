import os
import requests
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def generate_questions_from_groq(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return completion.choices[0].message.content


def fix_json_with_groq(raw_output: str) -> str:
    fix_prompt = f"""
You are a JSON repair assistant.
Convert the following text into valid JSON only.
Do not add explanation.
Do not add markdown.

Text:
{raw_output}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": fix_prompt}],
        temperature=0
    )
    return completion.choices[0].message.content
