from typing import List, Tuple


def build_question_prompt(
    role: str,
    job_description: str,
    retrieved_resume_chunks: List[Tuple[str, float]],
    question_count: int,
    difficulty: str
) -> str:
    resume_context_parts = []
    for idx, (chunk, score) in enumerate(retrieved_resume_chunks, start=1):
        resume_context_parts.append(
            f"Resume Chunk {idx} (relevance_score={round(float(score), 4)}):\n{chunk}"
        )
    resume_context = "\n\n".join(resume_context_parts)

    return f"""
You are an expert technical interviewer for a company hiring platform.

Generate personalized technical interview questions.

STRICT RULES:
1. Questions must be grounded in BOTH:
   - retrieved resume context
   - job description
2. Do NOT ask generic textbook questions.
3. Do NOT ask broad questions like:
   - What is Python?
   - What is SQL?
   - Tell me about yourself
4. Ask only role-relevant technical questions.
5. Prefer implementation, project, debugging, optimization, architecture, API, database, deployment, and real-experience based questions.
6. Each question must be unique.
7. Return ONLY valid JSON.
8. Do NOT return markdown.
9. Do NOT return explanation text.
10. expected_points must contain 3 to 5 short bullet-like strings.
11. Add category.
12. Add resume_reference and jd_reference.
13. Do not invent technologies that are not present in resume or JD.

ROLE:
{role}

JOB DESCRIPTION:
{job_description}

RETRIEVED RESUME CONTEXT:
{resume_context}

Generate exactly {question_count} questions.

Difficulty level for all questions: {difficulty}

Return JSON in exactly this format:
{{
  "questions": [
    {{
      "question_no": 1,
      "question": "string",
      "topic": "string",
      "category": "technical",
      "difficulty": "{difficulty}",
      "time_limit_sec": 90,
      "expected_points": ["point 1", "point 2", "point 3"],
      "resume_reference": {{
        "source": "resume",
        "snippet": "short matching snippet from retrieved resume context"
      }},
      "jd_reference": {{
        "source": "job_description",
        "snippet": "short matching requirement from job description"
      }}
    }}
  ]
}}
"""