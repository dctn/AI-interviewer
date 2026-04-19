def build_resume_analysis_prompt(cleaned_text: str) -> str:
    prompt = f"""Analyze this resume and extract the following information in valid JSON format:

{{"name": "candidate name",
 "email": "candidate email", 
 "phone": "candidate phone number",
 "summary": "2-3 sentence professional summary",
 "skills": ["list", "of", "key", "skills"],
 "projects": ["Project 1 title", "Project 2 title"],
 "education": ["Bachelor's in CS - University, Year", "Master's - University"],
 "experience": ["Company 1 - Role - Duration", "Company 2 - Role"],
 "certifications": ["AWS Certified", "Google Data Analytics"]}}

Resume content:
{cleaned_text}

Return ONLY valid JSON. No markdown, no explanations, no code blocks."""
    return prompt
