from typing import Any, Dict, List

from pydantic import BaseModel

from models.config_models import MetricDefinition
from models.workflow_state import AnalyticsResult, EvidenceReference


class AnalyticsEngineError(Exception):
    """Exception raised when analytics computation fails."""
    pass


class AnalyticsEngine:
    """Calculates configuration-driven aggregations over typed records safely."""
    
    @staticmethod
    def calculate(
        records: List[BaseModel],
        metric: MetricDefinition,
        requested_filters: Dict[str, Any],
        allowed_filters: List[str],
        dataset_reference: str
    ) -> AnalyticsResult:
        """Applies filters and aggregates records according to the MetricDefinition.
        
        Raises AnalyticsEngineError on validation or execution failure.
        """
        if not records:
            # If records are empty, we return a result of 0.0
            evidence = EvidenceReference(
                dataset_reference=dataset_reference,
                metric_id=metric.metric_id,
                record_count=0,
                applied_filters=requested_filters
            )
            return AnalyticsResult(
                metric_id=metric.metric_id,
                metric_name=metric.display_name,
                aggregation=metric.operation,
                source_field=metric.target_field,
                result_value=0.0,
                record_count=0,
                evidence=evidence
            )
            
        record_model = records[0].__class__
        
        # 1. Validate requested filters are in allowed list
        for f_field in requested_filters:
            if f_field not in allowed_filters:
                raise AnalyticsEngineError(
                    f"Filter field '{f_field}' is not allowed in configuration."
                )
            if f_field not in record_model.model_fields:
                raise AnalyticsEngineError(
                    f"Filter field '{f_field}' does not exist on schema '{record_model.__name__}'."
                )
                
        # 2. Filter records by requested filters
        filtered_records = []
        for r in records:
            match = True
            for f_field, f_val in requested_filters.items():
                record_val = getattr(r, f_field)
                # Handle comparison safely as string or exact type
                if record_val is None or str(record_val).strip().lower() != str(f_val).strip().lower():
                    match = False
                    break
            if match:
                filtered_records.append(r)
                
        # 3. Filter records by metric-defined filters (if any)
        merged_filters = dict(requested_filters)
        if metric.filter_field:
            if metric.filter_field not in record_model.model_fields:
                raise AnalyticsEngineError(
                    f"Metric filter field '{metric.filter_field}' does not exist on schema '{record_model.__name__}'."
                )
            metric_filtered = []
            for r in filtered_records:
                record_val = getattr(r, metric.filter_field)
                if record_val is not None and str(record_val).strip().lower() == str(metric.filter_value).strip().lower():
                    metric_filtered.append(r)
            filtered_records = metric_filtered
            merged_filters[metric.filter_field] = metric.filter_value
            
        # 4. Perform aggregate computation
        record_count = len(filtered_records)
        result_value = 0.0
        
        if metric.operation == "count":
            result_value = float(record_count)
        else:
            # Operations requiring target field (sum, average, min, max)
            if not metric.target_field:
                raise AnalyticsEngineError(
                    f"Metric '{metric.metric_id}' operation '{metric.operation}' requires target_field to be set."
                )
            if metric.target_field not in record_model.model_fields:
                raise AnalyticsEngineError(
                    f"Aggregation field '{metric.target_field}' does not exist on schema '{record_model.__name__}'."
                )
                
            # Extract numerical values
            vals = []
            for r in filtered_records:
                val = getattr(r, metric.target_field)
                if val is not None:
                    try:
                        vals.append(float(val))
                    except (ValueError, TypeError) as e:
                        raise AnalyticsEngineError(
                            f"Failed to cast value of '{metric.target_field}' to float: {e}"
                        )
            
            if not vals:
                result_value = 0.0
            elif metric.operation == "sum":
                result_value = sum(vals)
            elif metric.operation == "average":
                result_value = sum(vals) / len(vals)
            elif metric.operation == "min":
                result_value = min(vals)
            elif metric.operation == "max":
                result_value = max(vals)
            else:
                raise AnalyticsEngineError(f"Unsupported aggregation operation: '{metric.operation}'")
                
        # 5. Build response and evidence reference
        evidence = EvidenceReference(
            dataset_reference=dataset_reference,
            metric_id=metric.metric_id,
            record_count=record_count,
            applied_filters=merged_filters
        )
        
        return AnalyticsResult(
            metric_id=metric.metric_id,
            metric_name=metric.display_name,
            aggregation=metric.operation,
            source_field=metric.target_field,
            result_value=result_value,
            record_count=record_count,
            evidence=evidence
        )
