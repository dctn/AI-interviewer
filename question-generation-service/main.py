from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.question_generation import router as question_generation_router

app = FastAPI(
    title="AI Recruitment - RAG Question Generation Service",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(question_generation_router)