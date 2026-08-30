from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.memory.working_memory import WorkingMemory
from app.services.memory.long_term_memory import LongTermMemory
from app.services.memory.retrieval import MemoryRetrieval
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages both working and long-term memory"""
    
    def __init__(self, db: Session):
        """
        Initialize memory manager.
        
        Args:
            db: Database session
        """
        self.db = db
        self.long_term_memory = LongTermMemory(db)
        self.retrieval = MemoryRetrieval(db)
        self.working_memories: Dict[str, WorkingMemory] = {}
    
    def get_working_memory(self, session_id: str) -> WorkingMemory:
        """
        Get or create working memory for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            WorkingMemory instance
        """
        if session_id not in self.working_memories:
            self.working_memories[session_id] = WorkingMemory(session_id)
        
        # Clean up expired memories
        memory = self.working_memories[session_id]
        if memory.is_expired():
            del self.working_memories[session_id]
            self.working_memories[session_id] = WorkingMemory(session_id)
            memory = self.working_memories[session_id]
        
        return memory
    
    async def consolidate_session(
        self,
        candidate_id: int,
        session_id: str
    ) -> None:
        """
        Consolidate working memory to long-term memory at end of session.
        
        Args:
            candidate_id: Candidate ID
            session_id: Session ID
        """
        if session_id in self.working_memories:
            working_memory = self.working_memories[session_id]
            await self.long_term_memory.consolidate_working_memory(
                candidate_id=candidate_id,
                session_id=session_id,
                working_memory=working_memory.get_memory()
            )
            
            # Remove from working memory cache
            del self.working_memories[session_id]
            
            logger.info(f"Consolidated working memory for session {session_id}")
    
    async def retrieve_context(
        self,
        candidate_id: int,
        query: str,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from memory.
        
        Args:
            candidate_id: Candidate ID
            query: Search query
            session_id: Optional session ID
        
        Returns:
            List of relevant memories
        """
        # Get working memory if session provided
        working_context = []
        if session_id and session_id in self.working_memories:
            working_memory = self.working_memories[session_id]
            working_context = [{
                "type": "working_memory",
                "content": working_memory.get_memory(),
                "session_id": session_id
            }]
        
        # Get long-term memory
        long_term_context = await self.retrieval.retrieve_relevant_memory(
            candidate_id=candidate_id,
            query=query
        )
        
        return working_context + long_term_context

