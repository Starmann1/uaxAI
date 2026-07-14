# UAXAI Architecture Documentation

## Core Overview

UAXAI is a configuration-driven, API-first, multi-agent explainable AI platform. It utilizes LangGraph for orchestrating specialized agents that execute state mutations on a shared, strongly-typed Pydantic state model (`WorkflowState`).

```mermaid
flowchart TD
    Client["API client"] --> API["FastAPI API layer (api/main.py)"]
    API --> Graph["LangGraph Engine (graph/workflow.py)"]
    Graph --> Nodes["Workflow Nodes (graph/nodes.py)"]
    
    subgraph Agents["Cooperative Agents"]
        Nodes --> Supervisor["SupervisorAgent"]
        Nodes --> Intent["IntentAgent"]
        Nodes --> Planner["PlannerAgent"]
        Nodes --> Domain["DomainAgent"]
        Nodes --> Data["DataAgent"]
        Nodes --> Analytics["AnalyticsAgent"]
        Nodes --> Explainability["ExplainabilityAgent"]
        Nodes --> Response["ResponseAgent"]
    end
    
    subgraph Services["Services & Core Layer"]
        Data --> Registry["SchemaRegistry (services/schema_registry.py)"]
        Analytics --> Engine["AnalyticsEngine (services/analytics_engine.py)"]
        Response --> LLM["BaseLLMService (GeminiService / FakeLLMService)"]
        Domain --> Loader["ConfigLoader (services/config_loader.py)"]
    end

    subgraph DataStore["Data & Config"]
        Loader --> YAML["pharma.yaml / automotive.yaml"]
        Data --> CSV["batches.csv / production.csv"]
    end
```

---

## Request Sequence Flow

The diagram below illustrates the path of a POST request to `/v1/queries` requiring batch data analytics.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI API
    participant Graph as LangGraph Workflow
    participant Planner as PlannerAgent
    participant Data as DataAgent
    participant Analytics as AnalyticsAgent
    participant Explain as ExplainabilityAgent
    participant Response as ResponseAgent
    participant LLM as LLM Service (Gemini / Fake)

    Client->>API: POST /v1/queries (query, industry, filters)
    API->>API: Validate parameters against industry capabilities
    API->>Graph: Invoke Workflow (WorkflowState)
    Graph->>Planner: Plan routing intent
    Note over Planner: Classifies needs:<br/>requires_data=True<br/>requires_analytics=True
    Graph->>Data: Load CSV records
    Note over Data: Resolves schema from SchemaRegistry
    Graph->>Analytics: Calculate aggregates
    Note over Analytics: Calculates operations safely
    Graph->>Explain: Generate audit trail
    Note over Explain: Compiles agent timing & evidence reference
    Graph->>Response: Assemble final response
    Response->>LLM: Generate final text response
    LLM-->>Response: Response text
    Graph-->>API: Returns final WorkflowState
    API-->>Client: Returns JSON response + analytics_result + execution_trace
```
