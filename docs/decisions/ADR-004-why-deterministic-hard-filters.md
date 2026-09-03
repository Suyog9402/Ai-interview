# ADR-004: Why Deterministic Hard-Filtering Precedes LLM Scoring

## Context
In corporate recruiting workflows, job postings frequently mandate strict minimum requirements (e.g. minimum years of experience, specific domain certifications, required core tech stack). Relying exclusively on LLMs to enforce binary pass/fail constraints is non-deterministic and unnecessarily expensive.

## Options Considered
1. **Pure LLM End-to-End Scoring**
   - *Pros*: Single prompt evaluates both soft qualities and hard constraints.
   - *Cons*: Susceptible to prompt drift and hallucination on binary criteria; wastes significant API tokens evaluating unqualified candidates who fail basic job requirements.
2. **Deterministic Hard Filters Before LLM Evaluation (Chosen)**
   - *Pros*: 100% deterministic rule enforcement (e.g. `years_experience >= required_years`). Immediate early disqualification terminates the pipeline, saving token cost and reducing latency.
   - *Cons*: Requires structured schema extraction of resume attributes before filtering.

## Decision
We implemented **deterministic hard-filtering gates in the LangGraph workflow**. If a candidate fails mandatory hard constraints, the pipeline branches immediately to candidate summary generation with a clear disqualification reason, completely bypassing costly LLM multi-agent evaluation prompts.
