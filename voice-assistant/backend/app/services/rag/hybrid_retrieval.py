import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from app.services.interfaces.vector_store import VectorStoreInterface
from app.services.interfaces.reranker import RerankerInterface
from app.services.rag.citation_tracker import CitationTracker
from app.services.rag.bm25 import OkapiBM25
from app.core.config import settings
from app.core.exceptions import RAGException

logger = logging.getLogger(__name__)


class HybridRetrieval:
    """
    Hybrid Retrieval combining Dense Vector Search and Lexical Okapi BM25 with Reranking support.
    
    Formula:
      Score_hybrid = alpha * Norm(Score_vector) + (1 - alpha) * Norm(Score_BM25)
    """
    
    def __init__(
        self,
        resume_store: VectorStoreInterface,
        transcript_store: VectorStoreInterface,
        jd_store: VectorStoreInterface,
        alpha: float = 0.5,  # 0=BM25 only, 1=vector only
        top_k: int = 10,
        rerank_top_k: int = 5,
        reranker: Optional[RerankerInterface] = None
    ):
        self.resume_store = resume_store
        self.transcript_store = transcript_store
        self.jd_store = jd_store
        self.alpha = alpha
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        self.reranker = reranker
        self.bm25_engine = OkapiBM25(k1=1.5, b=0.75)
    
    async def retrieve(
        self,
        query: str,
        source_types: Optional[List[str]] = None,  # ["resume", "transcript", "jd"]
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid dense-vector and Okapi BM25 lexical retrieval.
        
        Args:
            query: Search query string.
            source_types: List of source types to search ("resume", "transcript", "jd").
            filters: Optional metadata filters.
        
        Returns:
            List of ranked results with citations and provenance metadata.
        """
        try:
            if source_types is None:
                source_types = ["resume", "transcript", "jd"]
            
            all_results: List[Dict[str, Any]] = []
            
            # 1. Dense Vector Search across requested stores
            if "resume" in source_types and self.resume_store:
                resume_results = await self.resume_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "resume", "type": "vector", "score": 0.8}
                    for doc in resume_results
                ])
            
            if "transcript" in source_types and self.transcript_store:
                transcript_results = await self.transcript_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "transcript", "type": "vector", "score": 0.8}
                    for doc in transcript_results
                ])
            
            if "jd" in source_types and self.jd_store:
                jd_results = await self.jd_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "jd", "type": "vector", "score": 0.8}
                    for doc in jd_results
                ])
            
            # If no candidate documents found in vector stores, return empty list
            if not all_results:
                return []

            # 2. Okapi BM25 Lexical Ranking over candidate document corpus
            documents = [r["document"] for r in all_results]
            self.bm25_engine.fit(documents)
            bm25_scores = [
                self.bm25_engine.score_document(self.bm25_engine.tokenize(query), i)
                for i in range(len(documents))
            ]
            
            # Normalize BM25 scores (min-max normalization to [0, 1])
            max_bm25 = max(bm25_scores) if bm25_scores else 0.0
            norm_bm25_scores = [
                (s / max_bm25) if max_bm25 > 0.0 else 0.0
                for s in bm25_scores
            ]

            # 3. Combine scores using configurable alpha weight
            combined = []
            for i, result in enumerate(all_results):
                vector_score = result.get("score", 0.5)
                bm25_score = norm_bm25_scores[i]
                hybrid_score = (self.alpha * vector_score) + ((1.0 - self.alpha) * bm25_score)
                
                combined.append({
                    "document": result["document"],
                    "source": result["source"],
                    "vector_score": vector_score,
                    "bm25_score": bm25_score,
                    "score": round(hybrid_score, 4)
                })

            # Sort by combined hybrid score descending
            combined.sort(key=lambda x: x["score"], reverse=True)
            
            # 4. Neural Reranking (optional extension module)
            if self.reranker:
                combined = await self._rerank_results(query, combined)
            
            # 5. Format results with citations
            final_results = []
            for result in combined[:self.rerank_top_k]:
                citation = CitationTracker.generate_citation(
                    result["document"],
                    result.get("score", 0.0)
                )
                final_results.append({
                    "document": result["document"],
                    "citation": citation,
                    "score": result.get("score", 0.0),
                    "source": result.get("source", "unknown")
                })
            
            logger.info(f"Retrieved {len(final_results)} hybrid results for query: {query[:50]}")
            return final_results
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}", exc_info=True)
            raise RAGException(f"Failed to retrieve: {str(e)}")
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using an external cross-encoder model if configured."""
        if not self.reranker:
            return results
        
        try:
            documents = [r["document"] for r in results]
            reranked_docs = await self.reranker.rerank(query, documents, top_k=self.rerank_top_k)
            
            reranked_results = []
            for doc in reranked_docs:
                original = next((r for r in results if r["document"].page_content == doc.page_content), None)
                if original:
                    reranked_results.append(original)
            
            return reranked_results if reranked_results else results
        except Exception as e:
            logger.warning(f"Reranking failed, falling back to hybrid order: {e}")
            return results
