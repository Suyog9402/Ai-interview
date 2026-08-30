from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.rag import RAGQuery, RAGResponse, RAGResult
from app.api.deps import get_current_active_user
from app.services.rag import get_rag_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ask", response_model=RAGResponse)
async def rag_query(
    query: RAGQuery,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Query RAG system with citations"""
    try:
        rag_service = get_rag_service()
        
        results = await rag_service.retrieve(
            query=query.query,
            source_types=query.source_types,
            filters=query.filters
        )
        
        # Convert to response format
        rag_results = []
        for result in results[:query.top_k] if query.top_k else results:
            rag_results.append(RAGResult(
                document_content=result["document"].page_content,
                citation=result["citation"],
                score=result["score"],
                source=result.get("source", "unknown")
            ))
        
        return RAGResponse(
            query=query.query,
            results=rag_results,
            total_results=len(rag_results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )

