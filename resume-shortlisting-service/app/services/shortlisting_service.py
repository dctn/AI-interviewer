import re
from app.core.config import SHORTLIST_THRESHOLD


def extract_keywords_from_jd(job_description: str):
    words = re.findall(r"[A-Za-z0-9\+\#\.]+", job_description.lower())

    stop_words = {
        "we", "are", "looking", "for", "with", "and", "the", "a", "an", "to", "of",
        "in", "on", "is", "be", "should", "have", "able", "will", "as", "or", "by",
        "candidate", "experience", "knowledge"
    }

    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return list(dict.fromkeys(keywords))


def perform_shortlisting(resume_analysis, role: str, job_description: str):
    resume_skills = [skill.lower() for skill in resume_analysis.skills]
    jd_keywords = extract_keywords_from_jd(job_description)

    matching_skills = []
    missing_skills = []

    for keyword in jd_keywords:
        matched = False

        # exact or partial skill match
        for skill in resume_skills:
            if keyword in skill or skill in keyword:
                matching_skills.append(keyword)
                matched = True
                break

        if not matched:
            if keyword in resume_analysis.raw_text.lower():
                matching_skills.append(keyword)
            else:
                missing_skills.append(keyword)

    total_keywords = len(jd_keywords) if jd_keywords else 1
    score = (len(matching_skills) / total_keywords) * 100

    shortlist_status = "shortlisted" if score >= SHORTLIST_THRESHOLD else "rejected"

    if shortlist_status == "shortlisted":
        feedback = "Your resume matches the job requirements sufficiently. You are shortlisted for the next round."
    else:
        if missing_skills:
            feedback = (
                "Your resume currently does not match the job requirements enough. "
                "Please improve these areas: " + ", ".join(missing_skills[:8])
            )
        else:
            feedback = "Your resume currently does not match the required job criteria sufficiently."

    return {
        "candidate_name": resume_analysis.name,
        "email": resume_analysis.email,
        "role": role,
        "shortlist_status": shortlist_status,
        "score": round(score, 2),
        "matching_skills": list(dict.fromkeys(matching_skills)),
        "missing_skills": list(dict.fromkeys(missing_skills)),
        "feedback": feedback
    }