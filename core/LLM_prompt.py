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
MUST INCLUDE ACCORDING TO RESUME AND CURRENT JOB MARKET:
- Minimum 15 specific required technical skills, tools, frameworks
- Specific years of experience (e.g. "3+ years with distributed systems")
- Specific technologies by name (e.g. AWS, Kubernetes, Java, Python, not just "cloud" or "programming")
- Responsibilities section with 6+ bullet points
- Preferred qualifications with specific certifications or tools

Role/Details: {detail}

Resume: {resume}

Be extremely specific. Never use vague terms like "programming languages" — always name them explicitly.
""")


from langchain_core.prompts import ChatPromptTemplate

PROMPT_question_generation = ChatPromptTemplate.from_template("""
You are a senior technical interviewer at a top tech company.

Your task is to generate highly relevant, non-generic interview questions based on:
- Candidate Resume
- Job Description
- Experience Level
- Difficulty Level

---

INPUTS:

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

EXPERIENCE LEVEL:
{experience_level}

DIFFICULTY:
{difficulty}

---

INSTRUCTIONS:

1. PERSONALIZATION (VERY IMPORTANT)
- Ask questions tailored to candidate’s actual skills and projects
- If a skill is present → ask deep questions on it
- If a key JD skill is missing → ask probing or gap-detection questions

2. QUESTION QUALITY
- Avoid generic questions like "What is Python?"
- Prefer:
  - scenario-based questions
  - real-world problem solving
  - follow-up style questions
  - "why" and "how" questions

3. DIFFICULTY CONTROL
- Easy → fundamentals, definitions, simple use cases
- Medium → practical problems, debugging, real scenarios
- Hard → system design, optimization, edge cases, trade-offs

4. EXPERIENCE CONTROL
- Fresher → basics + project discussion
- Junior → applied coding + debugging
- Mid → architecture decisions + scaling
- Senior → system design + trade-offs + leadership

5. COVERAGE REQUIREMENTS
Generate EXACTLY:
- 2 questions from candidate's strong skills
- 2 questions from JD required skills (even if missing)
- 2 behavioral or situational question

6. OUTPUT STYLE
- Questions must be clear, concise, and professional
- Each question must test a specific skill
- Questions must start with behavioral or self intro 
- Questions order is most important
- No explanations

---

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "questions": [
    {{
      "question": "<question text>",
      "type": "technical | behavioral | gap",
      "difficulty": "{difficulty}",
      "skill_target": "<specific skill being tested>"
      "category": "conceptual | practical | scenario | problem_solving | design | behavioral | domain_specific",
      "question_domain": "<broad domain like software, mechanical, civil, electrical, finance, marketing, hr, healthcare, etc.>",
      "sub_domain": "<specific area like React, Thermodynamics, Structural Analysis, SEO, Accounting, etc.>",      
    }}
  ]
}}

---

CRITICAL RULES:
- Do NOT include explanations
- Do NOT include extra text
- Do NOT repeat resume content
- Do NOT use vague wording
- MUST return valid JSON only
- MUST generate exactly 5 questions

If output is not valid JSON, the system will fail.
""")