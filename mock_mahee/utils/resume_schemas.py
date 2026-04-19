from typing import List, Any
from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
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
