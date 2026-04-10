def build_resume_analysis_prompt(resume_text: str) -> str:
    return f"""
You are an expert resume parser for a recruitment platform.

Your task is to analyze the resume text and return structured JSON only.

IMPORTANT RULES:
1. Return only valid JSON.
2. Do not include markdown.
3. Do not include explanation text.
4. If a field is missing, return empty string for string fields and empty list for list fields.
5. Extract only information clearly present in the resume text.
6. Do not hallucinate.

Return JSON exactly in this structure:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "summary": "string",
  "skills": ["skill1", "skill2"],
  "projects": ["project1", "project2"],
  "education": ["education1", "education2"],
  "experience": ["experience1", "experience2"],
  "certifications": ["cert1", "cert2"]
}}

Resume Text:
{resume_text}
"""