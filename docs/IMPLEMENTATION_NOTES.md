# Implementation Notes

## Phase 0 baseline

The existing repository is a Core Architecture Demonstration (CAD). It contains a
linear LangGraph workflow, two YAML industry configurations, CSV repositories,
seven focused agents, a Gemini service boundary, Streamlit demo, and unit tests.

This phase establishes reproducible development foundations only:

- Python tooling is declared in `pyproject.toml`.
- Local configuration and CSV data resolve from the project root rather than the
  current shell directory.
- `.env` and generated artifacts are ignored by Git.
- `.env.example` documents the optional Gemini key without exposing a secret.

## Intended MVP direction

The next phases will focus on the Pharmaceutical package. They will introduce
configuration-defined metrics and filters, a deterministic planner with
conditional LangGraph routing, structured explainability traces, and a FastAPI
API. They are intentionally not part of Phase 0.

## Explicitly deferred

PostgreSQL, RAG, vector search, authentication, RBAC, multi-tenancy, Redis,
Docker, MCP, background workers, and production telemetry are out of scope for
the v0.2 MVP.
