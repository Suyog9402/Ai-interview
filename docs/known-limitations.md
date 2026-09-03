# Known Limitations & Engineering Transparency

This document outlines architectural trade-offs, current design boundaries, and future roadmap areas to provide complete engineering transparency.

---

## 1. Speech Delivery Analysis Scope
- **Measurable Pacing vs Psychological Claims**: The speech analysis engine measures objective acoustic delivery characteristics: Words Per Minute (WPM), hesitation pause duration, filler-word frequency, and turn-taking response latency.
- **Explicit Boundary**: The system does **not** claim to detect emotional states, psychological confidence, or lie detection from acoustic audio, as such claims lack scientific consensus and reproducibility.

---

## 2. Storage Provider Interfaces
- **Active Backend**: Local filesystem storage (`app/services/storage/local.py`) is the active, production-tested storage engine for audio recordings and resume PDFs.
- **Cloud Adapters**: AWS S3, Azure Blob, and GCP Cloud Storage adapters (`app/services/storage/aws_s3.py`, etc.) are designed as pluggable interface contracts for enterprise cloud deployment, but are not active by default to prevent billing dependencies during local development and testing.

---

## 3. RAG Retrieval & Neural Reranking
- **Active Ranking**: Dense embeddings (Google `text-embedding-004` / OpenAI embeddings / local deterministic vectors) + pure-Python Okapi BM25 with normalized hybrid fusion.
- **Cross-Encoder Reranking**: The `RerankerInterface` is architected as an extensible plugin hook. Deep learning cross-encoder neural rerankers (e.g. `bge-reranker-large` / Cohere Rerank) can be plugged in without refactoring the retrieval pipeline.

---

## 4. Multi-Criteria Evaluation Pipeline Architecture
- **Resource Optimization**: Specialized evaluation criteria (Technical Accuracy, Problem Solving, Communication) execute structured prompting through the configured LLM rather than spinning up multiple independent heavy models, reducing API token consumption, latency, and operational cost.

---

## 5. Offline Fallback & Free-Tier Resiliency
- **Zero-Cost Operation**: The entire unit test suite (`pytest`) and RAG retrieval benchmark (`scripts/evaluate_rag.py`) operate 100% offline with zero external API calls or billing requirements.
- **Demo Mode**: In environments where external AI API keys (Groq, Gemini, Deepgram, OpenAI) are not configured or rate limits are exceeded, deterministic fallback extractors and mock assessment handlers ensure the application remains functional.
