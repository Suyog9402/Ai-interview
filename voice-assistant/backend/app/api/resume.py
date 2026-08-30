from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import shutil
from datetime import datetime
from ..services.rag_service import rag_service
from .deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/resume", tags=["resume"])

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a resume PDF file and process it for JD matching
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create user-specific directory
        user_upload_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{timestamp}.pdf"
        file_path = os.path.join(user_upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process resume with RAG service
        result = rag_service.process_resume(file_path, str(current_user.id))
        
        if "Error" in result:
            raise HTTPException(status_code=500, detail=result)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Resume uploaded and processed successfully",
                "filename": filename,
                "user_id": str(current_user.id)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")

@router.get("/match-jds")
async def get_jd_matches(
    threshold: float = 0.65,
    current_user: User = Depends(get_current_user)
):
    """
    Get job description matches for the user's uploaded resume
    """
    try:
        # Get matches from RAG service
        matches = rag_service.match_resume_with_jds(str(current_user.id), threshold)
        
        return JSONResponse(
            status_code=200,
            content={
                "matches": matches,
                "total_matches": len(matches),
                "threshold": threshold,
                "user_id": str(current_user.id)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting JD matches: {str(e)}")

@router.get("/jd/{jd_filename}")
async def get_jd_content(
    jd_filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the content of a specific job description file
    """
    try:
        content = rag_service.get_jd_content(jd_filename)
        
        if not content:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        return JSONResponse(
            status_code=200,
            content={
                "filename": jd_filename,
                "content": content
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting JD content: {str(e)}")

@router.post("/initialize-jds")
async def initialize_job_descriptions(
    current_user: User = Depends(get_current_user)
):
    """
    Initialize job descriptions in the vector store (admin function)
    """
    try:
        rag_service.load_job_descriptions()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Job descriptions loaded into vector store successfully"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing JDs: {str(e)}")

@router.get("/resume-status")
async def get_resume_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check if user has uploaded a resume
    """
    try:
        resume_content = rag_service.get_resume_content(str(current_user.id))
        
        return JSONResponse(
            status_code=200,
            content={
                "has_resume": len(resume_content) > 0,
                "user_id": str(current_user.id)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking resume status: {str(e)}") 