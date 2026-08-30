from app.services.vector_stores.base import BaseVectorStore
from app.services.vector_stores.chroma import ChromaVectorStore
from app.core.config import settings
from app.services.interfaces.vector_store import VectorStoreInterface
from app.core.exceptions import RAGException

# Future implementations
# from app.services.vector_stores.weaviate import WeaviateVectorStore
# from app.services.vector_stores.pgvector import PgVectorStore


def get_vector_store(collection_name: str) -> VectorStoreInterface:
    """
    Factory function to get the appropriate vector store based on config.
    
    Args:
        collection_name: Name of the collection to use
    
    Returns:
        Vector store instance
    """
    provider = settings.vector_store_provider.lower()
    
    if provider == "chroma":
        return ChromaVectorStore(
            persist_directory=settings.vector_store_path,
            collection_name=collection_name
        )
    elif provider == "weaviate":
        if not settings.weaviate_url:
            raise RAGException("Weaviate URL not configured")
        # return WeaviateVectorStore(
        #     url=settings.weaviate_url,
        #     api_key=settings.weaviate_api_key,
        #     collection_name=collection_name
        # )
        raise RAGException("Weaviate not yet implemented")
    elif provider == "pgvector":
        if not settings.pgvector_connection_string:
            raise RAGException("pgvector connection string not configured")
        # return PgVectorStore(
        #     connection_string=settings.pgvector_connection_string,
        #     collection_name=collection_name
        # )
        raise RAGException("pgvector not yet implemented")
    else:
        raise RAGException(f"Unknown vector store provider: {provider}")

__all__ = ["get_vector_store", "BaseVectorStore", "ChromaVectorStore"]

