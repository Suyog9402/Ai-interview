from app.services.rag.hybrid_retrieval import HybridRetrieval
from app.services.rag.citation_tracker import CitationTracker
from app.services.vector_stores import get_vector_store
from app.core.config import settings

__all__ = ["HybridRetrieval", "CitationTracker", "get_rag_service"]


def get_rag_service():
    """Factory function to get RAG service"""
    resume_store = get_vector_store(settings.vector_store_collection_resumes)
    transcript_store = get_vector_store(settings.vector_store_collection_transcripts)
    jd_store = get_vector_store(settings.vector_store_collection_jds)
    
    return HybridRetrieval(
        resume_store=resume_store,
        transcript_store=transcript_store,
        jd_store=jd_store,
        alpha=settings.rag_hybrid_alpha,
        top_k=settings.rag_retrieval_top_k,
        rerank_top_k=settings.rag_rerank_top_k
    )

