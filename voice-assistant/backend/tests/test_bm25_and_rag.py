"""
Unit Tests for Okapi BM25 Lexical Ranking & Hybrid Retrieval
Verifies tokenization, IDF calculations, length normalization, and score weighting with 0 API calls.
"""
import pytest
from langchain_core.documents import Document
from app.services.rag.bm25 import OkapiBM25
from app.services.rag.hybrid_retrieval import HybridRetrieval

def test_bm25_tokenization():
    text = "FastAPI, PostgreSQL & Docker-compose!"
    tokens = OkapiBM25.tokenize(text)
    assert "fastapi" in tokens
    assert "postgresql" in tokens
    assert "docker-compose" in tokens

def test_bm25_ranking_accuracy():
    docs = [
        Document(page_content="FastAPI is a modern Python web framework for building APIs."),
        Document(page_content="PostgreSQL is an open-source relational database management system."),
        Document(page_content="Docker automates application deployment inside software containers.")
    ]
    
    bm25 = OkapiBM25(k1=1.5, b=0.75)
    bm25.fit(docs)
    
    # Query matching doc 0
    results = bm25.search("FastAPI Python framework", top_k=3)
    assert len(results) > 0
    top_doc, top_score = results[0]
    assert "FastAPI" in top_doc.page_content
    assert top_score > 0.0

def test_bm25_idf_calculation():
    docs = [
        Document(page_content="Python Python Python web development"),
        Document(page_content="Python data science"),
        Document(page_content="Rust systems programming with no Python")
    ]
    bm25 = OkapiBM25()
    bm25.fit(docs)
    
    # 'Python' appears in all 3 docs, 'Rust' appears in only 1 doc -> IDF(Rust) should be higher than IDF(Python)
    assert bm25.idf.get("rust", 0.0) > bm25.idf.get("python", 0.0)

@pytest.mark.asyncio
async def test_hybrid_retrieval_empty_fallback():
    # Mock vector store returning empty results
    class MockVectorStore:
        async def similarity_search(self, *args, **kwargs):
            return []
            
    mock_store = MockVectorStore()
    hybrid = HybridRetrieval(
        resume_store=mock_store,
        transcript_store=mock_store,
        jd_store=mock_store,
        alpha=0.5
    )
    
    results = await hybrid.retrieve("test query")
    assert results == []
