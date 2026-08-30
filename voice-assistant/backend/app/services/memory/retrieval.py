from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.memory.long_term_memory import LongTermMemory
from app.services.rag import get_rag_service
import logging

logger = logging.getLogger(__name__)


class MemoryRetrieval:
    """Memory retrieval using RAG"""
    
    def __init__(self, db: Session):
        """
        Initialize memory retrieval.
        
        Args:
            db: Database session
        """
        self.db = db
        self.long_term_memory = LongTermMemory(db)
        self.rag_service = get_rag_service()
    
    async def retrieve_relevant_memory(
        self,
        candidate_id: int,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using RAG.
        
        Args:
            candidate_id: Candidate ID
            query: Search query
            context: Optional context for retrieval
        
        Returns:
            List of relevant memories with citations
        """
        try:
            # Use RAG to search across memory stores
            results = await self.rag_service.retrieve(
                query=query,
                source_types=["resume", "transcript"],  # Memory is stored in these
                filters={"candidate_id": candidate_id} if context else None
            )
            
            # Also search long-term memory directly
            memories = await self.long_term_memory.retrieve_memory(
                candidate_id=candidate_id,
                query=query,
                limit=5
            )
            
            # Combine and format results
            combined = []
            
            # Add RAG results
            for result in results:
                combined.append({
                    "type": "rag_result",
                    "content": result["document"].page_content,
                    "citation": result["citation"],
                    "score": result["score"]
                })
            
            # Add direct memory results
            for memory in memories:
                combined.append({
                    "type": "memory",
                    "content": memory.get("content", {}),
                    "metadata": memory.get("metadata", {}),
                    "session_id": memory.get("session_id"),
                    "score": 1.0  # Direct memory match
                })
            
            # Sort by score
            combined.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            
            return combined[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return []

