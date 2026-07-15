# UAXAI Platform Limitations & Deferred Features

The UAXAI Pharmaceutical MVP is designed as a focused, high-integrity architecture validation. The following features are explicitly out of scope for the current v0.2 project submission and have been deferred:

## 1. Out-of-Scope Features
* **Persistence & Databases**: The platform reads exclusively from local flat CSV files. No relational databases (e.g., PostgreSQL, SQLite), ORMs (SQLAlchemy), migrations (Alembic), or document stores are implemented.
* **Vector Search & RAG**: Knowledge extraction from PDFs or documentation remains purely domain terminology keyword configuration. Vector stores (pgvector, ChromaDB) and vector embeddings are not utilized.
* **Authentication & RBAC**: The FastAPI server has no login mechanisms, user accounts, JWT token validation, or role-based access control filters.
* **Multi-Tenancy**: The application assumes single-tenant isolation, with all requests operating under the same environment scope.
* **Caching Layer**: No Redis or in-memory caching is implemented for calculations or CSV parsing.
* **Model Context Protocol (MCP)**: Dynamic tool definitions or external API registries are not integrated.
* **Docker Containerization**: Container configuration (Dockerfile, Docker Compose) is deferred. The application runs locally using native Python environments.
* **Autonomous/Agentic Tool Execution**: Agents are routed deterministically via the planner node. Dynamic LLM tool calling or agent-driven shell/python tool execution is disabled for safety and predictability.
* **Background Queue Workers**: Analytics tasks run synchronously within the HTTP thread pool. No Celery, RQ, or RabbitMQ message brokers are wired in.
