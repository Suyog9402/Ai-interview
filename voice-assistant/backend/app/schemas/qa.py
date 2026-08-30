from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QAPairBase(BaseModel):
    question: str
    answer: str
    session_id: Optional[str] = None
    score: Optional[int] = None

class QAPairCreate(QAPairBase):
    pass

class QAPair(QAPairBase):
    id: int
    user_id: int
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True 