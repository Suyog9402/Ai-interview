from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.resume import router as resume_router
from app.api.qa import router as qa_router
from app.api.interview import router as interview_router
from app.api.face_detection import router as face_detection_router
from app.api.candidates import router as candidates_router
from app.api.recordings import router as recordings_router
from app.api.jds import router as jds_router
from app.api.matching import router as matching_router
from app.api.rag import router as rag_router
from app.api.admin import router as admin_router

api_router = APIRouter()

# Existing routes
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(resume_router)
api_router.include_router(qa_router)
api_router.include_router(interview_router)
api_router.include_router(face_detection_router)

# New production routes
api_router.include_router(candidates_router)
api_router.include_router(recordings_router)
api_router.include_router(jds_router)
api_router.include_router(matching_router)
api_router.include_router(rag_router)
api_router.include_router(admin_router)
