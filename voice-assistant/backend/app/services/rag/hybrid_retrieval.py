import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from app.services.interfaces.vector_store import VectorStoreInterface
from app.services.interfaces.reranker import RerankerInterface
from app.services.rag.citation_tracker import CitationTracker
from app.core.config import settings
from app.core.exceptions import RAGException

logger = logging.getLogger(__name__)


class HybridRetrieval:
    """Hybrid retrieval combining vector search and keyword search with reranking"""
    
    def __init__(
        self,
        resume_store: VectorStoreInterface,
        transcript_store: VectorStoreInterface,
        jd_store: VectorStoreInterface,
        alpha: float = 0.5,  # 0=keyword, 1=vector
        top_k: int = 10,
        rerank_top_k: int = 5,
        reranker: Optional[RerankerInterface] = None
    ):
        """
        Initialize hybrid retrieval.
        
        Args:
            resume_store: Vector store for resumes
            transcript_store: Vector store for transcripts
            jd_store: Vector store for job descriptions
            alpha: Hybrid weight (0=keyword only, 1=vector only)
            top_k: Number of results to retrieve
            rerank_top_k: Number of results after reranking
            reranker: Optional reranker implementation
        """
        self.resume_store = resume_store
        self.transcript_store = transcript_store
        self.jd_store = jd_store
        self.alpha = alpha
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
        self.reranker = reranker
    
    async def retrieve(
        self,
        query: str,
        source_types: Optional[List[str]] = None,  # ["resume", "transcript", "jd"]
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval.
        
        Args:
            query: Search query
            source_types: Optional list of source types to search
            filters: Optional metadata filters
        
        Returns:
            List of results with citations
        """
        try:
            if source_types is None:
                source_types = ["resume", "transcript", "jd"]
            
            all_results = []
            
            # Vector search from each source
            if "resume" in source_types:
                resume_results = await self.resume_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "resume", "type": "vector"}
                    for doc in resume_results
                ])
            
            if "transcript" in source_types:
                transcript_results = await self.transcript_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "transcript", "type": "vector"}
                    for doc in transcript_results
                ])
            
            if "jd" in source_types:
                jd_results = await self.jd_store.similarity_search(
                    query=query,
                    k=self.top_k,
                    filters=filters
                )
                all_results.extend([
                    {"document": doc, "source": "jd", "type": "vector"}
                    for doc in jd_results
                ])
            
            # Keyword search (simplified BM25-like scoring)
            keyword_results = await self._keyword_search(query, all_results)
            
            # Combine vector and keyword results
            combined = self._combine_results(all_results, keyword_results, self.alpha)
            
            # Rerank if reranker available
            if self.reranker:
                combined = await self._rerank_results(query, combined)
            
            # Add citations
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
            
            logger.info(f"Retrieved {len(final_results)} results for query: {query[:50]}")
            return final_results
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}", exc_info=True)
            raise RAGException(f"Failed to retrieve: {str(e)}")
    
    async def _keyword_search(
        self,
        query: str,
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search (simplified).
        
        In production, you'd use BM25 or similar.
        For now, we score based on keyword matches in document content.
        """
        query_terms = query.lower().split()
        keyword_results = []
        
        for result in vector_results:
            doc = result["document"]
            content_lower = doc.page_content.lower()
            
            # Count matching terms
            matches = sum(1 for term in query_terms if term in content_lower)
            score = matches / len(query_terms) if query_terms else 0.0
            
            keyword_results.append({
                **result,
                "keyword_score": score,
                "type": "keyword"
            })
        
        return keyword_results
    
    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        alpha: float
    ) -> List[Dict[str, Any]]:
        """
        Combine vector and keyword results using hybrid scoring.
        
        Args:
            vector_results: Vector search results
            keyword_results: Keyword search results
            alpha: Weight for vector (1-alpha for keyword)
        
        Returns:
            Combined and scored results
        """
        # Create a map of document IDs to results
        combined_map = {}
        
        # Add vector results
        for result in vector_results:
            doc_id = id(result["document"])  # Use document ID
            combined_map[doc_id] = {
                **result,
                "vector_score": result.get("score", 0.0) if "score" in result else 0.5,
                "keyword_score": 0.0
            }
        
        # Update with keyword scores
        for result in keyword_results:
            doc_id = id(result["document"])
            if doc_id in combined_map:
                combined_map[doc_id]["keyword_score"] = result.get("keyword_score", 0.0)
            else:
                combined_map[doc_id] = {
                    **result,
                    "vector_score": 0.0,
                    "keyword_score": result.get("keyword_score", 0.0)
                }
        
        # Calculate hybrid scores
        combined = []
        for result in combined_map.values():
            hybrid_score = (
                alpha * result.get("vector_score", 0.0) +
                (1 - alpha) * result.get("keyword_score", 0.0)
            )
            result["score"] = hybrid_score
            combined.append(result)
        
        # Sort by hybrid score
        combined.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        return combined
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using reranker if available.
        
        Args:
            query: Search query
            results: Results to rerank
        
        Returns:
            Reranked results
        """
        if not self.reranker:
            return results
        
        try:
            documents = [r["document"] for r in results]
            reranked_docs = await self.reranker.rerank(query, documents, top_k=self.rerank_top_k)
            
            # Create new results with reranked order
            reranked_results = []
            doc_map = {id(doc): doc for doc in documents}
            
            for doc in reranked_docs:
                doc_id = id(doc)
                # Find original result
                original = next((r for r in results if id(r["document"]) == doc_id), None)
                if original:
                    reranked_results.append(original)
            
            return reranked_results
            
        except Exception as e:
            logger.warning(f"Reranking failed, using original results: {e}")
            return results

