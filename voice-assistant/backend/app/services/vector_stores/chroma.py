import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.services.vector_stores.base import BaseVectorStore
from app.core.config import settings
from app.core.exceptions import RAGException
import logging

logger = logging.getLogger(__name__)


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation"""
    
    def __init__(self, persist_directory: str, collection_name: str):
        """
        Initialize ChromaDB vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        super().__init__()
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embeddings
        if not settings.openai_api_key:
            raise RAGException("OpenAI API key not configured for embeddings")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key
        )
        
        # Initialize ChromaDB
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
    
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add documents to ChromaDB.
        
        Args:
            documents: List of Document objects
            collection_name: Optional collection name (uses instance collection if not provided)
            metadata: Optional metadata to add to all documents
        
        Returns:
            List of document IDs
        """
        try:
            # Add metadata to documents if provided
            if metadata:
                for doc in documents:
                    if doc.metadata:
                        doc.metadata.update(metadata)
                    else:
                        doc.metadata = metadata
            
            # Add documents
            ids = self.vector_store.add_documents(documents)
            
            # Persist
            self.vector_store.persist()
            
            logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}", exc_info=True)
            raise RAGException(f"Failed to add documents: {str(e)}")
    
    async def similarity_search(
        self,
        query: str,
        k: int = 10,
        collection_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search in ChromaDB.
        
        Args:
            query: Search query text
            k: Number of results to return
            collection_name: Optional collection name (ignored, uses instance collection)
            filters: Optional metadata filters (ChromaDB where clause)
        
        Returns:
            List of similar documents
        """
        try:
            search_kwargs = {"k": k}
            if filters:
                search_kwargs["where"] = filters
            
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                **search_kwargs
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}", exc_info=True)
            raise RAGException(f"Failed to perform similarity search: {str(e)}")
    
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Delete documents from ChromaDB.
        
        Args:
            document_ids: List of document IDs to delete
            collection_name: Optional collection name (ignored)
        
        Returns:
            True if successful
        """
        try:
            self.vector_store.delete(ids=document_ids)
            self.vector_store.persist()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}", exc_info=True)
            raise RAGException(f"Failed to delete documents: {str(e)}")
    
    async def update_document(
        self,
        document_id: str,
        document: Document,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Update a document in ChromaDB.
        
        Args:
            document_id: ID of document to update
            document: Updated document
            collection_name: Optional collection name (ignored)
        
        Returns:
            True if successful
        """
        try:
            # Delete old document
            await self.delete_documents([document_id])
            
            # Add updated document with same ID
            self.vector_store.add_documents([document], ids=[document_id])
            self.vector_store.persist()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {e}", exc_info=True)
            raise RAGException(f"Failed to update document: {str(e)}")
    
    async def get_collection_names(self) -> List[str]:
        """
        Get list of collection names.
        
        Note: ChromaDB doesn't have a direct way to list collections,
        so we return the current collection name.
        
        Returns:
            List containing current collection name
        """
        return [self.collection_name]

