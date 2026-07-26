# UAXAI Demo Script

Use the following HTTP requests to demonstrate the capabilities and dynamic routing of the UAXAI Pharmaceutical Platform.

Ensure the server is running first:
```powershell
uvicorn api.main:app --reload
```

---

## 1. Demo Query A: Average Batch Yield

Calculates the average batch yield for batches associated with `Bioreactor Alpha`.

### Request
```powershell
$body = @{
  query = "What is the average batch yield?"
  industry = "pharma"
  metric_id = "average_batch_yield"
  filters = @{ reactor_id = "Bioreactor Alpha" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/queries `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 12
```

### Expected Output Fields
* `status`: `"COMPLETED"`
* `intent`: `"ANALYZE"`
* `analytics_result.result_value`: `90.15`
* `analytics_result.record_count`: `8`
* `execution_trace.events`: Should show events for `SupervisorAgent`, `IntentAgent`, `PlannerAgent`, `DomainAgent`, `DataAgent`, `AnalyticsAgent`, `ExplainabilityAgent`, and `ResponseAgent`.

---

## 2. Demo Query B: Failed Batch Count

Counts the number of failed batches from `Bioreactor Alpha`.

### Request
```powershell
$body = @{
  query = "How many batches failed?"
  industry = "pharma"
  metric_id = "failed_batch_count"
  filters = @{ reactor_id = "Bioreactor Alpha" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/queries `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 12
```

### Expected Output Fields
* `status`: `"COMPLETED"`
* `intent`: `"ANALYZE"`
* `analytics_result.result_value`: `2.0` (for batch IDs BAT-004 and BAT-008)
* `analytics_result.record_count`: `2`
* `explainability_summary`: References `"quality_status=Fail"` and dataset provenance.

---

## 3. Demo Query C: Unsupported Query

Submits an out-of-scope query. Illustrates planner-level routing skipping Data and Analytics extraction.

### Request
```powershell
$body = @{
  query = "Predict next month's medicine sales."
  industry = "pharma"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/queries `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 12
```

### Expected Output Fields
* `status`: `"UNSUPPORTED"`
* `intent`: `"UNSUPPORTED"`
* `plan.requires_data`: `false`
* `plan.requires_analytics`: `false`
* `analytics_result`: `null`
* `execution_trace.events`: Contains only `SupervisorAgent`, `IntentAgent`, `PlannerAgent`, and `ResponseAgent`. (Crucially, `DataAgent` and `AnalyticsAgent` are completely skipped).
* `final_response`: Tells the user that sales predictions are not supported.
