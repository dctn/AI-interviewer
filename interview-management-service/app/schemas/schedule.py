from pydantic import BaseModel, EmailStr
from typing import Optional


class ScheduleCreate(BaseModel):
    candidate_name: str
    email: EmailStr
    role: str
    interview_date: str
    interview_time: str
    status: str = "scheduled"


class ScheduleUpdate(BaseModel):
    candidate_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    status: Optional[str] = None


class ScheduleResponse(BaseModel):
    id: int
    candidate_name: str
    email: str
    role: str
    interview_date: str
    interview_time: str
    status: str
    created_at: str