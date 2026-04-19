from groq import Groq
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_resume_with_groq(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )
    return response.choices[0].message.content


def fix_resume_json_with_groq(raw_output: str):
    fix_prompt = f"""Fix this JSON output to be valid JSON:

{raw_output}

Return ONLY valid JSON, no explanations."""
    return analyze_resume_with_groq(fix_prompt)
