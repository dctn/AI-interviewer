from typing import List, Optional, Any
from pydantic import BaseModel


class ResumeAnalysisInput(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    skills: List[str]
    projects: List[str]
    education: List[str]
    experience: List[str]
    certifications: List[str]
    raw_text: str


class ShortlistRequest(BaseModel):
    role: str
    job_description: str
    resume_analysis: ResumeAnalysisInput


class ShortlistResponse(BaseModel):
    candidate_name: str
    email: str
    role: str
    shortlist_status: str
    score: float
    matching_skills: List[str]
    missing_skills: List[str]
    feedback: str
    schedule: Optional[Any] = None