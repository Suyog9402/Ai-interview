from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.db.database import engine, Base
from app.core.config import settings

# Import all models to ensure they're registered with Base
from app.models import (
    user, qa, interview, candidate, recording, jd, matching, admin, memory
)

# Create database tables for all models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware (production origin allowed for face analysis / API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Interview Assistant API",
        "version": settings.version,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"} 