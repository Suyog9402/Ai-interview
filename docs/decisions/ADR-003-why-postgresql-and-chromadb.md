# ADR-003: Why PostgreSQL + ChromaDB Hybrid Storage

## Context
The AI Interview Assistant manages two fundamentally different data profiles:
1. Structured, transactional entity data (user credentials, candidate metadata, question records, audit logs).
2. Unstructured text chunks requiring high-dimensional vector embeddings for semantic similarity search.

## Options Considered
1. **Single Relational Database (PostgreSQL + pgvector)**
   - *Pros*: Single database engine to maintain.
   - *Cons*: Additional extensions and complex vector indexing configurations for lightweight local prototyping.
2. **PostgreSQL (Transactional) + ChromaDB (Vector Store) (Chosen)**
   - *Pros*: Clear separation of concerns. PostgreSQL handles ACID transactions, relational foreign keys, and administrative queries via SQLAlchemy. ChromaDB runs locally with zero setup overhead for fast HNSW approximate nearest neighbor search.
   - *Cons*: Two separate storage subsystems to manage during backup operations.

## Decision
We chose a **hybrid persistence model**. PostgreSQL serves as the authoritative source of truth for all business entities, while ChromaDB provides localized, fast vector indexing for Job Descriptions, resumes, and interview transcripts.
