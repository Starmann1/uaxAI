import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies import get_llm_service
from api.schemas import CapabilitiesResponse, QueryRequest, QueryResponse
from graph.workflow import create_workflow
from services.base_llm_service import BaseLLMService
from services.config_loader import ConfigurationError, list_industries, load_industry_config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("uaxai-api")

app = FastAPI(
    title="Universal Agentic Explainable AI (uaxAI) API",
    description="Thin API layer for config-driven multi-agent pharmaceutical batch analytics",
    version="0.1.0"
)

# CORS middleware for accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to avoid leaking raw exceptions."""
    logger.exception("Unhandled error occurred in API endpoint")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."}
    )


@app.get("/healthz", response_model=dict)
def health_check():
    """Returns the service health status."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/v1/industries", response_model=List[dict])
def get_industries():
    """Lists metadata for all configured industries."""
    keys = list_industries()
    results = []
    for key in keys:
        try:
            config = load_industry_config(key)
            results.append({
                "industry_name": config.industry_name,
                "display_name": config.display_name,
                "metric": config.metric
            })
        except ConfigurationError as e:
            logger.warning(f"Failed to load config for industry '{key}': {e}")
            
    return results


@app.get("/v1/industries/{industry}/capabilities", response_model=CapabilitiesResponse)
def get_industry_capabilities(industry: str):
    """Returns the configured metrics and allowed filters for a specific industry."""
    if industry not in list_industries():
        raise HTTPException(
            status_code=404,
            detail=f"Industry '{industry}' is not supported on this platform."
        )
        
    try:
        config = load_industry_config(industry)
        return CapabilitiesResponse(
            industry=config.industry_name,
            metrics=[m.metric_id for m in config.metrics],
            allowed_filters=config.allowed_filters
        )
    except ConfigurationError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load configuration for industry '{industry}': {e}"
        )


@app.post("/v1/queries", response_model=QueryResponse)
def run_query(request: QueryRequest, llm_service: BaseLLMService = Depends(get_llm_service)):
    """Executes a query through the multi-agent workflow for the pharmaceutical industry."""
    # 1. Validate industry is supported
    industries = list_industries()
    if request.industry not in industries:
        raise HTTPException(
            status_code=400,
            detail=f"Industry '{request.industry}' is not supported. Supported: {industries}"
        )
        
    # 2. Load config and validate metrics and filter fields
    try:
        config = load_industry_config(request.industry)
    except ConfigurationError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration load failed: {e}"
        )
        
    # Validate metric_id if provided
    if request.metric_id:
        metric_ids = [m.metric_id for m in config.metrics]
        if request.metric_id not in metric_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Metric ID '{request.metric_id}' is not allowed. Allowed: {metric_ids}"
            )
            
    # Validate filters if provided
    if request.filters:
        for filter_key in request.filters:
            if filter_key not in config.allowed_filters:
                raise HTTPException(
                    status_code=400,
                    detail=f"Filter field '{filter_key}' is not allowed. Allowed: {config.allowed_filters}"
                )
                
    # 3. Construct and execute workflow graph
    workflow = create_workflow(llm_service=llm_service)
    
    # We invoke the graph with input state dict
    inputs = {
        "query": request.query,
        "industry": request.industry,
        "requested_metric_id": request.metric_id,
        "requested_filters": request.filters or {}
    }
    
    logger.info(f"Invoking workflow for query: '{request.query}' (Industry: {request.industry})")
    
    try:
        result_state = workflow.invoke(inputs)
    except Exception as e:
        logger.exception("Workflow invocation crashed unexpectedly")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution crashed: {e}"
        )
        
    # 4. Map output response schemas
    status_raw = result_state.get("status") or "FAILED"
    status_mapped = "COMPLETED" if status_raw in ("VALIDATED", "COMPLETED") else status_raw
    
    explainability_summary = None
    explainability_output = result_state.get("explainability_output")
    if explainability_output:
        if isinstance(explainability_output, dict):
            explainability_summary = explainability_output.get("trace_summary")
        else:
            explainability_summary = getattr(explainability_output, "trace_summary", None)
        
    errors = None
    if status_mapped == "FAILED":
        errors = [result_state.get("final_response") or "Unknown workflow failure occurred."]
        
    return QueryResponse(
        correlation_id=result_state["correlation_id"],
        status=status_mapped,
        final_response=result_state.get("final_response"),
        intent=result_state.get("intent"),
        plan=result_state.get("execution_plan"),
        analytics_result=result_state.get("analytics_result"),
        explainability_summary=explainability_summary,
        execution_trace=result_state.get("execution_trace"),
        errors=errors
    )
