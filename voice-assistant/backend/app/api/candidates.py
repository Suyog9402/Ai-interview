from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse, ResumeCreate, ResumeResponse
from app.models.candidate import Candidate, Resume
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new candidate"""
    try:
        # Check if candidate already exists for this user
        existing = db.query(Candidate).filter(
            Candidate.user_id == candidate.user_id,
            Candidate.email == candidate.email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate with this email already exists"
            )
        
        db_candidate = Candidate(**candidate.dict())
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
        
        return db_candidate
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create candidate: {str(e)}"
        )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get candidate by ID"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    update_data = candidate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/{candidate_id}/resume", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    candidate_id: int,
    resume: ResumeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Upload candidate resume"""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    db_resume = Resume(
        candidate_id=candidate_id,
        file_path=resume.file_path,
        file_version=1
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    return db_resume


@router.get("/{candidate_id}/resumes", response_model=List[ResumeResponse])
async def get_candidate_resumes(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all resumes for a candidate"""
    resumes = db.query(Resume).filter(Resume.candidate_id == candidate_id).all()
    return resumes

