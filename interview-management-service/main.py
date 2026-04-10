from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.schedules import router as schedules_router
from app.api.routes.dashboard import router as dashboard_router
from app.db.database import create_tables

app = FastAPI(
    title="Interview Management Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(health_router)
app.include_router(schedules_router)
app.include_router(dashboard_router)