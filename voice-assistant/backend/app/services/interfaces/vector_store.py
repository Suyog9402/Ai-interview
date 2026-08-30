from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document


class VectorStoreInterface(ABC):
    """Interface for vector store providers (ChromaDB, Weaviate, pgvector)"""
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects
            collection_name: Name of the collection
            metadata: Optional metadata to add to all documents
        
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 10,
        collection_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query text
            k: Number of results to return
            collection_name: Optional collection name
            filters: Optional metadata filters
        
        Returns:
            List of similar documents
        """
        pass
    
    @abstractmethod
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            document_ids: List of document IDs to delete
            collection_name: Optional collection name
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def update_document(
        self,
        document_id: str,
        document: Document,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Update a document in the vector store.
        
        Args:
            document_id: ID of document to update
            document: Updated document
            collection_name: Optional collection name
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_collection_names(self) -> List[str]:
        """
        Get list of collection names.
        
        Returns:
            List of collection names
        """
        pass

