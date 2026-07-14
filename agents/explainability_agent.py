import datetime

from agents.base_agent import BaseAgent
from models.workflow_state import ExplainabilityOutput, WorkflowState


class ExplainabilityAgent(BaseAgent):
    """Explainability Agent: Builds a transparent audit trace from structured execution events and evidence."""
    
    @property
    def name(self) -> str:
        return "ExplainabilityAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        steps = list(state.execution_history)
        if self.name not in steps:
            steps.append(self.name)
            
        trace_lines = ["UAXAI Platform Execution Trace Audit:"]
        
        # Build explanation from structured trace events if available
        if state.execution_trace and state.execution_trace.events:
            for idx, event in enumerate(state.execution_trace.events, 1):
                try:
                    start_dt = datetime.datetime.fromisoformat(event.started_at)
                    comp_dt = datetime.datetime.fromisoformat(event.completed_at)
                    duration_ms = int((comp_dt - start_dt).total_seconds() * 1000)
                    duration_str = f"{duration_ms}ms"
                except Exception:
                    duration_str = "unknown duration"
                    
                status_str = "succeeded" if event.outcome == "SUCCESS" else "FAILED"
                trace_lines.append(f"  Step {idx}: {event.agent_name} {status_str} (duration: {duration_str}).")
                if event.error_message:
                    trace_lines.append(f"    Error: {event.error_message}")
        else:
            # Fallback to legacy execution history list
            for idx, step in enumerate(steps, 1):
                trace_lines.append(f"  Step {idx}: {step} executed successfully.")
                
        # Append analytics evidence details if available
        if state.analytics_result:
            res = state.analytics_result
            trace_lines.append("\nAnalytics Evidence Provenance:")
            trace_lines.append(f"  Dataset: {res.evidence.dataset_reference}")
            trace_lines.append(f"  Metric ID: {res.metric_id}")
            trace_lines.append(f"  Metric Name: {res.metric_name}")
            trace_lines.append(f"  Aggregation: {res.aggregation}")
            if res.source_field:
                trace_lines.append(f"  Target Field: {res.source_field}")
            trace_lines.append(f"  Record Count: {res.record_count}")
            if res.evidence.applied_filters:
                filters_str = ", ".join(f"{k}={v}" for k, v in res.evidence.applied_filters.items())
                trace_lines.append(f"  Applied Filters: {filters_str}")
                
        trace_summary = "\n".join(trace_lines)
        
        state.explainability_output = ExplainabilityOutput(
            trace_summary=trace_summary,
            steps_executed=steps
        )
        
        return state
