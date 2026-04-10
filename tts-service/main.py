from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes.health import router as health_router
from app.api.routes.tts import router as tts_router
import os

app = FastAPI(
    title="TTS Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("audio_outputs", exist_ok=True)

app.mount("/audio", StaticFiles(directory="audio_outputs"), name="audio")

app.include_router(health_router)
app.include_router(tts_router)