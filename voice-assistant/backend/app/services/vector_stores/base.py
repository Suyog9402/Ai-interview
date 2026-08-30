from app.services.interfaces.vector_store import VectorStoreInterface
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document


class BaseVectorStore(VectorStoreInterface):
    """Base class for vector store implementations"""
    
    def __init__(self):
        """Initialize base vector store"""
        pass
    
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def similarity_search(
        self,
        query: str,
        k: int = 10,
        collection_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: Optional[str] = None
    ) -> bool:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def update_document(
        self,
        document_id: str,
        document: Document,
        collection_name: Optional[str] = None
    ) -> bool:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def get_collection_names(self) -> List[str]:
        """Base implementation - should be overridden"""
        raise NotImplementedError

