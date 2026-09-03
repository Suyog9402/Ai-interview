# ADR-005: Why Hybrid Retrieval (Vector + Okapi BM25) for RAG Grounding

## Context
When assessing technical interviews, queries often contain specialized acronyms, library names (e.g. `gRPC`, `Alembic`, `FastAPI`, `WebRTC`), and exact technical terms. Dense embeddings alone can suffer from semantic drift or fail to prioritize exact keyword matches, while keyword search alone misses conceptual paraphrasing.

## Options Considered
1. **Dense Vector Search Only**
   - *Pros*: Excellent semantic generalization and synonym handling.
   - *Cons*: Weak on rare acronyms, specific version numbers, and exact technical token matching.
2. **Sparse Lexical Search Only (BM25)**
   - *Pros*: Precise on exact token occurrences and specialized jargon.
   - *Cons*: Blind to synonyms, paraphrasing, and semantic concepts.
3. **Hybrid Retrieval (Vector + Okapi BM25) (Chosen)**
   - *Pros*: Captures both semantic meaning and exact keyword occurrences. Normalizes and combines scores with a configurable alpha weighting parameter ($\alpha=0.5$).
   - *Cons*: Requires executing both vector distance and BM25 token matching over candidate text chunks.

## Decision
We implemented **Hybrid Retrieval combining ChromaDB dense vectors and pure-Python Okapi BM25**. Our offline benchmark (`evaluate_rag.py`) demonstrates that Hybrid Retrieval achieves superior Mean Reciprocal Rank (MRR) and Recall@5 compared to either standalone retrieval strategy.
