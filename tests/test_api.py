from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_get_industries():
    response = client.get("/v1/industries")
    assert response.status_code == 200
    industries = response.json()
    assert any(i["industry_name"] == "pharma" for i in industries)
    assert any(i["industry_name"] == "automotive" for i in industries)


def test_get_pharma_capabilities():
    response = client.get("/v1/industries/pharma/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["industry"] == "pharma"
    assert "average_batch_yield" in data["metrics"]
    assert "failed_batch_count" in data["metrics"]
    assert "reactor_id" in data["allowed_filters"]


def test_get_nonexistent_capabilities():
    response = client.get("/v1/industries/nonexistent/capabilities")
    assert response.status_code == 404
    assert "not supported" in response.json()["detail"]


def test_query_average_batch_yield():
    payload = {
        "query": "What is the average batch yield?",
        "industry": "pharma",
        "metric_id": "average_batch_yield",
        "filters": {"reactor_id": "Bioreactor Alpha"}
    }
    response = client.post("/v1/queries", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["intent"] == "ANALYZE"
    assert data["correlation_id"] is not None
    assert data["plan"] is not None
    assert data["analytics_result"] is not None
    assert data["analytics_result"]["result_value"] == 90.15
    assert data["analytics_result"]["record_count"] == 8
    assert data["explainability_summary"] is not None
    assert "Analytics Evidence Provenance:" in data["explainability_summary"]
    assert "Dataset: data/pharma/batches.csv" in data["explainability_summary"]


def test_query_failed_batch_count():
    payload = {
        "query": "How many batches failed?",
        "industry": "pharma",
        "metric_id": "failed_batch_count",
        "filters": {"reactor_id": "Bioreactor Alpha"}
    }
    response = client.post("/v1/queries", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["intent"] == "ANALYZE"
    assert data["analytics_result"]["result_value"] == 2.0
    assert data["analytics_result"]["record_count"] == 2
    assert "quality_status=Fail" in data["explainability_summary"]


def test_query_invalid_metric():
    payload = {
        "query": "What is the average batch yield?",
        "industry": "pharma",
        "metric_id": "invalid_metric_id"
    }
    response = client.post("/v1/queries", json=payload)
    assert response.status_code == 400
    assert "Metric ID 'invalid_metric_id' is not allowed" in response.json()["detail"]


def test_query_forbidden_filter():
    payload = {
        "query": "What is the average batch yield?",
        "industry": "pharma",
        "metric_id": "average_batch_yield",
        "filters": {"invalid_filter_key": "val"}
    }
    response = client.post("/v1/queries", json=payload)
    assert response.status_code == 400
    assert "Filter field 'invalid_filter_key' is not allowed" in response.json()["detail"]
