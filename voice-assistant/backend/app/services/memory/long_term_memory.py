from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.memory import MemoryStore
from app.models.candidate import Candidate
from app.core.config import settings
from app.services.vector_stores import get_vector_store
from langchain_core.documents import Document
import json
import logging

logger = logging.getLogger(__name__)


class LongTermMemory:
    """Long-term memory storage and retrieval"""
    
    def __init__(self, db: Session):
        """
        Initialize long-term memory.
        
        Args:
            db: Database session
        """
        self.db = db
        self.vector_store = get_vector_store("memory")
        self.retention_days = settings.memory_long_term_retention_days
    
    async def store_memory(
        self,
        candidate_id: int,
        session_id: str,
        content: Dict[str, Any],
        memory_type: str = "long_term"
    ) -> MemoryStore:
        """
        Store memory in database and vector store.
        
        Args:
            candidate_id: Candidate ID
            session_id: Session ID
            content: Memory content
            memory_type: Type of memory (working/long_term)
        
        Returns:
            MemoryStore database object
        """
        try:
            # Create memory store record
            memory_store = MemoryStore(
                candidate_id=candidate_id,
                session_id=session_id,
                memory_type=memory_type,
                content=content,
                metadata_json={
                    "stored_at": datetime.now().isoformat(),
                    "retention_days": self.retention_days
                }
            )
            
            self.db.add(memory_store)
            self.db.flush()
            
            # Create document for vector store
            doc_content = self._content_to_text(content)
            document = Document(
                page_content=doc_content,
                metadata={
                    "candidate_id": candidate_id,
                    "session_id": session_id,
                    "memory_type": memory_type,
                    "memory_id": memory_store.id,
                    "stored_at": datetime.now().isoformat()
                }
            )
            
            # Store in vector store
            await self.vector_store.add_documents([document])
            
            self.db.commit()
            self.db.refresh(memory_store)
            
            logger.info(f"Stored {memory_type} memory for candidate {candidate_id}, session {session_id}")
            return memory_store
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing memory: {e}", exc_info=True)
            raise
    
    async def retrieve_memory(
        self,
        candidate_id: int,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a candidate.
        
        Args:
            candidate_id: Candidate ID
            query: Optional search query
            memory_type: Optional memory type filter
            limit: Maximum number of results
        
        Returns:
            List of memory dictionaries
        """
        try:
            # Build filters
            filters = {"candidate_id": candidate_id}
            if memory_type:
                filters["memory_type"] = memory_type
            
            # If query provided, use vector search
            if query:
                documents = await self.vector_store.similarity_search(
                    query=query,
                    k=limit,
                    filters=filters
                )
                
                # Get memory IDs from documents
                memory_ids = [
                    int(doc.metadata.get("memory_id"))
                    for doc in documents
                    if doc.metadata.get("memory_id")
                ]
                
                # Fetch from database
                memories = self.db.query(MemoryStore).filter(
                    MemoryStore.id.in_(memory_ids)
                ).limit(limit).all()
            else:
                # Direct database query
                query_obj = self.db.query(MemoryStore).filter(
                    MemoryStore.candidate_id == candidate_id
                )
                
                if memory_type:
                    query_obj = query_obj.filter(MemoryStore.memory_type == memory_type)
                
                memories = query_obj.order_by(
                    MemoryStore.created_at.desc()
                ).limit(limit).all()
            
            # Convert to dictionaries
            return [
                {
                    "id": mem.id,
                    "session_id": mem.session_id,
                    "memory_type": mem.memory_type,
                    "content": mem.content,
                    "metadata": mem.metadata_json,
                    "created_at": mem.created_at.isoformat() if mem.created_at else None
                }
                for mem in memories
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
            return []
    
    async def consolidate_working_memory(
        self,
        candidate_id: int,
        session_id: str,
        working_memory: Dict[str, Any]
    ) -> MemoryStore:
        """
        Consolidate working memory into long-term memory.
        
        Args:
            candidate_id: Candidate ID
            session_id: Session ID
            working_memory: Working memory dictionary
        
        Returns:
            Stored memory object
        """
        # Extract significant insights
        consolidated = {
            "session_id": session_id,
            "skill_coverage": working_memory.get("skill_coverage", {}),
            "candidate_profile": working_memory.get("candidate_profile", {}),
            "key_insights": self._extract_key_insights(working_memory),
            "consolidated_at": datetime.now().isoformat()
        }
        
        return await self.store_memory(
            candidate_id=candidate_id,
            session_id=session_id,
            content=consolidated,
            memory_type="long_term"
        )
    
    def _extract_key_insights(self, working_memory: Dict[str, Any]) -> List[str]:
        """Extract key insights from working memory"""
        insights = []
        
        # Add significant strengths
        strengths = working_memory.get("candidate_profile", {}).get("strengths", [])
        for strength in strengths[:5]:  # Top 5
            insights.append(f"Strength: {strength.get('strength', '')}")
        
        # Add significant weaknesses
        weaknesses = working_memory.get("candidate_profile", {}).get("weaknesses", [])
        for weakness in weaknesses[:5]:  # Top 5
            insights.append(f"Weakness: {weakness.get('weakness', '')}")
        
        return insights
    
    def _content_to_text(self, content: Dict[str, Any]) -> str:
        """Convert memory content to text for vector storage"""
        # Convert structured content to searchable text
        text_parts = []
        
        if "skill_coverage" in content:
            covered_skills = [
                skill for skill, data in content["skill_coverage"].items()
                if data.get("covered", False)
            ]
            text_parts.append(f"Skills: {', '.join(covered_skills)}")
        
        if "candidate_profile" in content:
            profile = content["candidate_profile"]
            if profile.get("strengths"):
                text_parts.append(f"Strengths: {', '.join([s.get('strength', '') for s in profile['strengths']])}")
            if profile.get("weaknesses"):
                text_parts.append(f"Weaknesses: {', '.join([w.get('weakness', '') for w in profile['weaknesses']])}")
        
        if "key_insights" in content:
            text_parts.extend(content["key_insights"])
        
        return "\n".join(text_parts)
    
    async def cleanup_expired_memories(self) -> int:
        """
        Clean up expired memories.
        
        Returns:
            Number of memories deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            expired = self.db.query(MemoryStore).filter(
                MemoryStore.created_at < cutoff_date,
                MemoryStore.memory_type == "long_term"
            ).all()
            
            count = len(expired)
            
            for memory in expired:
                # Delete from vector store if possible
                # (would need to track document IDs)
                self.db.delete(memory)
            
            self.db.commit()
            
            logger.info(f"Cleaned up {count} expired memories")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up memories: {e}", exc_info=True)
            return 0

