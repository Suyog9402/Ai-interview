from typing import Dict, Any, List
from langchain_core.documents import Document


class CitationTracker:
    """Tracks citations for RAG retrieval results"""
    
    @staticmethod
    def generate_citation(document: Document, score: float = 0.0) -> Dict[str, Any]:
        """
        Generate citation for a document.
        
        Args:
            document: Document object
            score: Relevance score
        
        Returns:
            Citation dictionary
        """
        metadata = document.metadata or {}
        
        citation = {
            "source": metadata.get("source_type", "unknown"),
            "location": {
                "chunk_id": metadata.get("chunk_id"),
                "timestamp": metadata.get("timestamp"),
                "jd_section": metadata.get("jd_section"),
                "resume_section": metadata.get("resume_section"),
                "transcript_segment": metadata.get("transcript_segment")
            },
            "confidence": score,
            "page_content": document.page_content[:200]  # First 200 chars
        }
        
        return citation
    
    @staticmethod
    def add_citations_to_results(results: List[Document], scores: List[float] = None) -> List[Dict[str, Any]]:
        """
        Add citations to retrieval results.
        
        Args:
            results: List of documents
            scores: Optional list of scores
        
        Returns:
            List of results with citations
        """
        if scores is None:
            scores = [0.0] * len(results)
        
        cited_results = []
        for doc, score in zip(results, scores):
            cited_result = {
                "document": doc,
                "citation": CitationTracker.generate_citation(doc, score),
                "score": score
            }
            cited_results.append(cited_result)
        
        return cited_results

