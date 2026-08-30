from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.qa import QAPair
from app.schemas.qa import QAPairCreate, QAPair as QAPairSchema
from app.models.user import User
from app.api.deps import get_current_user
from app.services.rag_service import rag_service

router = APIRouter(prefix="/qa", tags=["qa"])

@router.post("/", response_model=QAPairSchema)
def create_qa_pair(
    qa: QAPairCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_qa = QAPair(
        user_id=user.id,
        question=qa.question,
        answer=qa.answer,
        session_id=qa.session_id
    )
    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)
    return db_qa

@router.post("/score", response_model=QAPairSchema)
def score_transcript(
    qa: QAPairCreate = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Use RAGService to evaluate the answer and get a score
    transcript = qa.answer
    score = rag_service.score_transcript(transcript)
    db_qa = QAPair(
        user_id=user.id,
        question=qa.question,
        answer=qa.answer,
        session_id=qa.session_id,
        score=score
    )
    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)
    return db_qa

@router.get("/", response_model=list[QAPairSchema])
def list_qa_pairs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(QAPair).filter(QAPair.user_id == user.id).all() 