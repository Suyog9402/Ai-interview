"""
Pure Python Okapi BM25 Ranking Algorithm

Implements the standard Okapi BM25 lexical ranking algorithm for documents and text chunks
with zero external API or library dependencies.

Formula:
  Score(D, Q) = SUM_i [ IDF(q_i) * (f(q_i, D) * (k1 + 1)) / (f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl))) ]
  IDF(q_i) = ln((N - n(q_i) + 0.5) / (n(q_i) + 0.5) + 1.0)
"""
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document

class OkapiBM25:
    """Standard Okapi BM25 ranking model for lexical retrieval."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize Okapi BM25.
        
        Args:
            k1: Term frequency saturation parameter (typically 1.2 - 2.0). Default 1.5.
            b: Document length normalization parameter (typically 0.75). Default 0.75.
        """
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.documents: List[Document] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple lowercase alphanumeric tokenization."""
        if not text:
            return []
        tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        # Filter single character non-alphanumeric tokens
        return [t for t in tokens if len(t) > 1 or t.isalnum()]

    def fit(self, documents: List[Document]):
        """
        Index a corpus of documents to calculate IDF and document length statistics.
        
        Args:
            documents: List of LangChain Document objects.
        """
        self.documents = documents
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            return

        self.doc_lengths = []
        self.doc_term_freqs = []
        self.doc_freqs = {}

        total_length = 0
        for doc in documents:
            tokens = self.tokenize(doc.page_content)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            # Term frequency for this document
            tf: Dict[str, int] = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            self.doc_term_freqs.append(tf)

            # Document frequency (number of docs containing token)
            for token in tf.keys():
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_len = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Calculate Okapi IDF for each unique token in the corpus
        self.idf = {}
        for token, df in self.doc_freqs.items():
            # Standard smoothed Okapi IDF
            self.idf[token] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

    def score_document(self, query_tokens: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a specific document index against query tokens."""
        if doc_idx >= len(self.doc_term_freqs) or self.avg_doc_len == 0:
            return 0.0

        doc_len = self.doc_lengths[doc_idx]
        tf_dict = self.doc_term_freqs[doc_idx]
        score = 0.0

        len_norm = 1.0 - self.b + self.b * (doc_len / self.avg_doc_len)

        for token in query_tokens:
            if token not in tf_dict:
                continue
            tf = tf_dict[token]
            idf = self.idf.get(token, 0.1)
            # Okapi BM25 formula
            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * len_norm
            score += idf * (numerator / denominator)

        return score

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Search the indexed corpus and return ranked (document, score) pairs.
        
        Args:
            query: Query string.
            top_k: Max results to return.
            
        Returns:
            List of (Document, score) tuples sorted descending by BM25 score.
        """
        query_tokens = self.tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        scored_docs: List[Tuple[Document, float]] = []
        for i, doc in enumerate(self.documents):
            score = self.score_document(query_tokens, i)
            if score > 0.0:
                scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]
