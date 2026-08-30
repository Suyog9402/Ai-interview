from abc import ABC, abstractmethod
from typing import List, Optional
from typing import List, Dict, Any
from langchain_core.documents import Document


class RerankerInterface(ABC):
    """Interface for reranking providers"""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None
    ) -> List[Document]:
        """
        Rerank documents based on query relevance.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Optional number of top results to return
        
        Returns:
            Reranked list of documents
        """
        pass
    
    @abstractmethod
    async def score(
        self,
        query: str,
        document: Document
    ) -> float:
        """
        Score a single document against a query.
        
        Args:
            query: Search query
            document: Document to score
        
        Returns:
            Relevance score (higher is better)
        """
        pass

