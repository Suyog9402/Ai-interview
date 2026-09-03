# ADR-002: Why LangGraph Over Linear LangChain Chains

## Context
Post-interview candidate assessment requires a multi-step evaluation workflow: audio transcription, quality gates, resume extraction, hard-filter checking, hybrid RAG grounding, and multi-agent scoring. Linear DAG chains (like basic LangChain `SequentialChain`) fail when cyclical retry loops or conditional early exits are required.

## Options Considered
1. **Linear LangChain Chains (`RunnableSequence`)**
   - *Pros*: Simple setup for unidirectional input-output flows.
   - *Cons*: Cannot handle loops (e.g. retranscribing poor audio), lacks first-class state checkpointing, and cannot branch dynamically without hacky custom wrappers.
2. **LangGraph StateGraph (Chosen)**
   - *Pros*: Cyclic graph modeling, explicit state schema (`InterviewPipelineState`), conditional router edges, state persistence/checkpoints, and modular node isolation.
   - *Cons*: Slightly steeper initial configuration curve.

## Decision
We chose **LangGraph**. Its stateful cyclic architecture enables:
- Quality verification gates with automated retry loops (`transcribe` -> `check_quality` -> `retranscribe`).
- Cost-saving conditional exits (bypassing expensive LLM evaluations if hard filters fail).
- Checkpointed state inspection for auditability and debugging.
