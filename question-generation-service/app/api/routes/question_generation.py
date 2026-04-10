from fastapi import APIRouter, HTTPException
from app.schemas.question_generation import (
    QuestionGenerationRequest,
    QuestionGenerationResponse
)
from app.pipelines.question_pipeline import run_question_generation_pipeline

router = APIRouter(tags=["Question Generation"])


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
def generate_questions(request: QuestionGenerationRequest):
    try:
        return run_question_generation_pipeline(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))