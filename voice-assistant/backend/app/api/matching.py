from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.matching import MatchResultResponse, MatchRequest
from app.models.matching import MatchResult
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/match", response_model=MatchResultResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    request: MatchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create match result (typically called by workflow)"""
    # This endpoint is mainly for manual matching if needed
    # Usually matching is done as part of the workflow
    from app.services.matching.engine import MatchingEngine
    from app.models.candidate import Resume
    from app.services.extraction import get_extractor
    
    # Get resume data
    resume = db.query(Resume).filter(
        Resume.candidate_id == request.candidate_id
    ).order_by(Resume.created_at.desc()).first()
    
    if not resume or not resume.extracted_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume data not available. Please extract resume data first."
        )
    
    # For transcript data, we'd need to get it from the session
    # For now, use empty transcript data
    transcript_data = {}
    
    matching_engine = MatchingEngine(db)
    match_result = await matching_engine.match_candidate_to_jd(
        candidate_id=request.candidate_id,
        jd_id=request.jd_id,
        resume_data=resume.extracted_data,
        transcript_data=transcript_data,
        session_id=request.session_id
    )
    
    return match_result


@router.get("/{candidate_id}/{jd_id}", response_model=MatchResultResponse)
async def get_match_result(
    candidate_id: int,
    jd_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get match result with evidence"""
    query = db.query(MatchResult).filter(
        MatchResult.candidate_id == candidate_id,
        MatchResult.jd_id == jd_id
    )
    
    if session_id:
        query = query.filter(MatchResult.session_id == session_id)
    
    match_result = query.order_by(MatchResult.created_at.desc()).first()
    
    if not match_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match result not found"
        )
    
    return match_result


@router.get("/candidate/{candidate_id}", response_model=List[MatchResultResponse])
async def get_candidate_matches(
    candidate_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all match results for a candidate"""
    matches = db.query(MatchResult).filter(
        MatchResult.candidate_id == candidate_id
    ).offset(skip).limit(limit).all()
    
    return matches

