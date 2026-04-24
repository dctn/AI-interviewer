from langchain_core.prompts import ChatPromptTemplate

PROMPT_resume_analysis = ChatPromptTemplate.from_template("""
You are a strict technical recruiter. Evaluate the resume against the JD.

DOMAIN CHECK FIRST:
- If resume domain ≠ JD domain → domain_match=false, overall_score<25, shortlist_verdict="No"

SCORE FLOORS (mandatory, not optional):
- kw_score>=75% → overall_score>=70
- kw_score>=60% → overall_score>=55
- kw_score>=45% → overall_score>=40
- kw_score<45%  → overall_score<=50

VERDICTS:
- overall_score>=80 AND kw_score>=70 → "Strong Yes"
- overall_score>=65 → "Yes"
- overall_score>=45 → "Maybe"
- overall_score<45  → "No"

KEYWORD EVIDENCE:
- Match: {kw_score}% ({matched_count}/{total_keywords})
- Found: {matched_keywords}
- Missing: {missing_keywords}

RESUME: {resume}
JD: {jd}

Score this resume against the job description.
Return ONLY this JSON, no explanation:
{{
  "overall_score": <0-100 int>,
  "skills_match": <0-100 int>,
  "experience_match": <0-100 int>,
  "education_match": <0-100 int>,
  "shortlist_verdict": "Strong Yes" | "Yes" | "Maybe" | "No",
  "domain_match": true | false,
  "keyword_match_pct": <use the pre-calculated value above>,
  "matching_skills": [<top 5 most critical matching skills>],
  "missing_skills": [<top 5 most critical missing skills>],
  "strong_points": [<what actually impressed you>],
  "improvement_tips": [<specific actionable resume fixes>],
  "predicted_interview_questions": [< top 5 Predicted Interview Questions>],
  "recruiter_note": "<one brutally honest sentence a recruiter would say>"
}}


CRITICAL INSTRUCTION:
- Do NOT include any text outside the JSON
- Do NOT repeat resume content
- Do NOT include bullet points or explanations
- Do NOT include tags like <resume> or </resume>
- ONLY return the JSON object
- Do not include special characters like \\n or anything
If you output anything else, the system will fail.

FINAL INSTRUCTION: 
Provide your response strictly in JSON format. 
Start with '{{' and end with '}}'. 
DO NOT include any tags like </resume> or preamble text.
""")


PROMPT_keyword = ChatPromptTemplate.from_template(
    """Extract all technical skills, tools, frameworks,
            and domain keywords from this job description.
            Return ONLY a JSON array of strings. No explanation.

            JD: {jd}"""
)

PROMPT_jd = ChatPromptTemplate.from_template("""
Generate a detailed Job Description for the following role as seen on top tech company careers page  or also search job seeking platform like linkedin.
Take resume data to know about current user and compare data details with jd to generate Job Description
MUST INCLUDE:
- Minimum 15 specific required technical skills, tools, frameworks
- Specific years of experience (e.g. "3+ years with distributed systems")
- Specific technologies by name (e.g. AWS, Kubernetes, Java, Python, not just "cloud" or "programming")
- Responsibilities section with 6+ bullet points
- Preferred qualifications with specific certifications or tools

Role/Details: {detail}

Resume: {resume}

Be extremely specific. Never use vague terms like "programming languages" — always name them explicitly.
""")