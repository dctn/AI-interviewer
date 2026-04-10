import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.pipelines.resume_analysis_pipeline import run_resume_analysis_pipeline
from app.integrations.question_generation_client import call_question_generation_service

router = APIRouter(tags=["Resume Analysis"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze-resume")
def analyze_resume(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = run_resume_analysis_pipeline(file_path)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-and-generate-questions")
def analyze_and_generate_questions(
    file: UploadFile = File(...),
    role: str = Form(...),
    job_description: str = Form(...),
    question_count: int = Form(5),
    difficulty: str = Form("medium")
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resume_analysis_result = run_resume_analysis_pipeline(file_path)

        generated_questions = call_question_generation_service(
            role=role,
            job_description=job_description,
            resume_text=resume_analysis_result.raw_text,
            question_count=question_count,
            difficulty=difficulty
        )

        return {
            "resume_analysis": resume_analysis_result,
            "generated_questions": generated_questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))