from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_optional_user
from app.services.rag_service import rag_service
from app.services.interview_service import InterviewService
from app.schemas.interview import InterviewSessionCreate, InterviewResultResponse
from typing import List, Dict, Any, Optional
import os
import json

router = APIRouter(prefix="/interview", tags=["interview"])

@router.post("/evaluate", response_model=InterviewResultResponse)
async def evaluate_interview(
    session_data: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Evaluate a complete interview session and return detailed results
    """
    try:
        # Create interview service instance
        interview_service = InterviewService()
        
        # Use a default user ID if not authenticated
        user_id = current_user.id if current_user else 1
        
        # Process the interview session
        result = await interview_service.evaluate_session(
            user_id=user_id,
            session_id=session_data.session_id,
            conversation=session_data.conversation,
            questions=session_data.questions,
            answers=session_data.answers,
            db=db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating interview: {str(e)}"
        )

@router.get("/history", response_model=List[InterviewResultResponse])
async def get_interview_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get user's interview history
    """
    try:
        interview_service = InterviewService()
        user_id = current_user.id if current_user else 1
        history = await interview_service.get_user_history(
            user_id=user_id,
            db=db
        )
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching interview history: {str(e)}"
        )

@router.get("/history/latest", response_model=InterviewResultResponse)
async def get_latest_interview(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get user's latest interview result
    """
    try:
        interview_service = InterviewService()
        user_id = current_user.id if current_user else 1
        history = await interview_service.get_user_history(
            user_id=user_id,
            db=db
        )
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail="No interview results found. Please complete an interview first."
            )
        
        # Return the most recent interview (first in the list since it's ordered by created_at desc)
        return history[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching latest interview: {str(e)}"
        )

@router.get("/{session_id}", response_model=InterviewResultResponse)
async def get_interview_result(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get specific interview result by session ID
    """
    try:
        interview_service = InterviewService()
        user_id = current_user.id if current_user else 1
        result = await interview_service.get_session_result(
            session_id=session_id,
            user_id=user_id,
            db=db
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )
            
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching interview result: {str(e)}"
        ) 

# --- Dynamic JD selection for LiveKit interviewer ---

@router.post("/select-jd")
async def select_interview_jd(
    payload: Dict[str, Any]
):
    """
    Set the selected JD filename to drive LiveKit interview questions.
    Expects payload: { "jd_filename": "backend_developer_senior.txt" }
    """
    try:
        jd_filename = payload.get("jd_filename", "").strip()
        if not jd_filename:
            raise HTTPException(status_code=400, detail="jd_filename is required")

        # Validate that the questions file exists
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        questions_dir = os.path.join(backend_dir, "interview_questions")
        questions_path = os.path.join(questions_dir, jd_filename)
        if not os.path.exists(questions_path):
            raise HTTPException(status_code=404, detail="Questions file not found for given jd_filename")

        # Persist the selection to a file read by the LiveKit worker
        selected_path = os.path.join(backend_dir, "selected_jd.txt")
        with open(selected_path, "w", encoding="utf-8") as f:
            f.write(jd_filename)

        return {"status": "ok", "jd_filename": jd_filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting JD: {str(e)}")

@router.get("/selected-jd")
async def get_selected_interview_jd():
    """
    Get the currently selected JD filename that the LiveKit worker will use.
    """
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        selected_path = os.path.join(backend_dir, "selected_jd.txt")
        if os.path.exists(selected_path):
            with open(selected_path, "r", encoding="utf-8") as f:
                jd_filename = f.read().strip()
            return {"jd_filename": jd_filename}
        return {"jd_filename": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading selected JD: {str(e)}")

@router.get("/available-question-files")
async def list_available_question_files():
    """
    List all available question files in interview_questions/.
    """
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        questions_dir = os.path.join(backend_dir, "interview_questions")
        if not os.path.isdir(questions_dir):
            return {"files": []}
        files = [f for f in os.listdir(questions_dir) if f.endswith(".txt")]
        return {"files": sorted(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing question files: {str(e)}")

@router.post("/select-best-from-matches")
async def select_best_questions_from_matches(payload: Dict[str, Any]):
    """
    Given RAG matches, pick the best available questions file and set it for LiveKit.
    Accepts payload with one of:
      - { "matches": [ { "jd_source": "backend_developer.txt" , ...}, ... ] } (sorted best-first optional)
      - { "jd_sources": ["backend_developer.txt", "full_stack_developer.txt", ...] } (ordered best-first)
    Returns the selected filename or 404 if none exist.
    """
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        questions_dir = os.path.join(backend_dir, "interview_questions")
        if not os.path.isdir(questions_dir):
            raise HTTPException(status_code=404, detail="questions directory not found")

        candidates: list[str] = []
        if isinstance(payload.get("matches"), list):
            for m in payload["matches"]:
                src = (m.get("jd_source") or "").strip()
                if src.endswith(".txt"):
                    candidates.append(src)
        if isinstance(payload.get("jd_sources"), list):
            for src in payload["jd_sources"]:
                s = (src or "").strip()
                if s.endswith(".txt"):
                    candidates.append(s)

        # Deduplicate preserving order
        seen = set()
        ordered = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                ordered.append(c)

        # Pick the first that exists
        for filename in ordered:
            path = os.path.join(questions_dir, filename)
            if os.path.exists(path):
                # write selection
                selected_path = os.path.join(backend_dir, "selected_jd.txt")
                with open(selected_path, "w", encoding="utf-8") as f:
                    f.write(filename)
                return {"status": "ok", "jd_filename": filename}

        raise HTTPException(status_code=404, detail="No matching questions file found for provided candidates")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting from matches: {str(e)}")