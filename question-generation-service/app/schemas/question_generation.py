from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class QuestionGenerationRequest(BaseModel):
    role: str = Field(..., min_length=2)
    job_description: str = Field(..., min_length=10)
    resume_text: str = Field(..., min_length=10)
    question_count: int = Field(default=5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")


class ReferenceItem(BaseModel):
    source: str
    snippet: str


class QuestionItem(BaseModel):
    question_no: int = Field(..., ge=1)
    question: str = Field(..., min_length=5)
    topic: str = Field(..., min_length=2)
    category: str = Field(default="technical")
    difficulty: Literal["easy", "medium", "hard"]
    time_limit_sec: int = Field(..., ge=30, le=600)
    expected_points: List[str] = Field(..., min_length=1)
    resume_reference: Optional[ReferenceItem] = None
    jd_reference: Optional[ReferenceItem] = None


class QuestionGenerationResponse(BaseModel):
    questions: List[QuestionItem]