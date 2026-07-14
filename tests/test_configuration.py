import pytest

from services.config_loader import ConfigurationError, list_industries, load_industry_config


def test_load_valid_configs():
    # Test valid automotive config
    auto_cfg = load_industry_config("automotive")
    assert auto_cfg.industry_name == "automotive"
    assert "Overall Equipment Effectiveness (OEE)" in auto_cfg.terminology
    assert auto_cfg.metric == "Overall Equipment Effectiveness (OEE)"
    assert auto_cfg.dataset_reference == "data/automotive/production.csv"
    assert auto_cfg.record_schema == "automotive_production"
    
    # Test valid pharma config
    pharma_cfg = load_industry_config("pharma")
    assert pharma_cfg.industry_name == "pharma"
    assert "Batch Yield Percentage" in pharma_cfg.terminology
    assert pharma_cfg.metric == "Batch Yield Percentage"
    assert pharma_cfg.dataset_reference == "data/pharma/batches.csv"
    assert pharma_cfg.record_schema == "pharmaceutical_batch"
    assert len(pharma_cfg.metrics) == 4
    
    # Verify metric mappings
    metric_ids = [m.metric_id for m in pharma_cfg.metrics]
    assert "batch_yield_sum" in metric_ids
    assert "average_batch_yield" in metric_ids
    assert "failed_batch_count" in metric_ids
    assert "batch_count" in metric_ids


def test_list_industries():
    industries = list_industries()
    assert "automotive" in industries
    assert "pharma" in industries


def test_load_missing_config():
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("nonexistent")
    assert "Configuration file not found" in str(exc_info.value)


def test_load_invalid_yaml(tmp_path):
    # Create an invalid YAML file
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("invalid_yaml: [unclosed brackets", encoding="utf-8")
    
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("invalid", config_dir=str(tmp_path))
    assert "Failed to parse YAML file" in str(exc_info.value)


def test_load_invalid_schema(tmp_path):
    # Create a YAML file that misses required fields (e.g. metric)
    invalid_schema_file = tmp_path / "missing_fields.yaml"
    invalid_schema_file.write_text("""
industry_name: "missing"
display_name: "Missing Fields"
terminology: ["A"]
entity_list: ["B"]
# metric and dataset_reference are missing
""", encoding="utf-8")
    
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("missing_fields", config_dir=str(tmp_path))
    assert "Failed to validate configuration" in str(exc_info.value)


def test_invalid_aggregation_fails(tmp_path):
    invalid_agg_file = tmp_path / "invalid_agg.yaml"
    invalid_agg_file.write_text("""
industry_name: "invalid_agg"
display_name: "Invalid Aggregation"
terminology: ["A"]
entity_list: ["B"]
metric: "A"
dataset_reference: "data/pharma/batches.csv"
record_schema: "pharmaceutical_batch"
metrics:
  - metric_id: "invalid_metric"
    operation: "invalid_operation"
    display_name: "Invalid Metric"
""", encoding="utf-8")
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("invalid_agg", config_dir=str(tmp_path))
    assert "Failed to validate configuration" in str(exc_info.value)


def test_unknown_record_schema_fails(tmp_path):
    unknown_schema_file = tmp_path / "unknown_schema.yaml"
    unknown_schema_file.write_text("""
industry_name: "unknown_schema"
display_name: "Unknown Schema"
terminology: ["A"]
entity_list: ["B"]
metric: "A"
dataset_reference: "data/pharma/batches.csv"
record_schema: "nonexistent_schema"
metrics: []
""", encoding="utf-8")
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("unknown_schema", config_dir=str(tmp_path))
    assert "Unknown record schema identifier" in str(exc_info.value)


def test_duplicate_metric_ids_fail(tmp_path):
    dup_metric_file = tmp_path / "dup_metrics.yaml"
    dup_metric_file.write_text("""
industry_name: "dup_metrics"
display_name: "Duplicate Metrics"
terminology: ["A"]
entity_list: ["B"]
metric: "A"
dataset_reference: "data/pharma/batches.csv"
record_schema: "pharmaceutical_batch"
metrics:
  - metric_id: "batch_count"
    operation: "count"
    display_name: "Batch Count"
  - metric_id: "batch_count"
    operation: "count"
    display_name: "Duplicate Batch Count"
""", encoding="utf-8")
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("dup_metrics", config_dir=str(tmp_path))
    assert "Duplicate metric ID found in configuration" in str(exc_info.value)


def test_invalid_fields_fail(tmp_path):
    invalid_fields_file = tmp_path / "invalid_fields.yaml"
    invalid_fields_file.write_text("""
industry_name: "invalid_fields"
display_name: "Invalid Fields"
terminology: ["A"]
entity_list: ["B"]
metric: "A"
dataset_reference: "data/pharma/batches.csv"
record_schema: "pharmaceutical_batch"
metrics:
  - metric_id: "bad_metric"
    operation: "sum"
    target_field: "non_existent_field"
    display_name: "Bad Metric"
""", encoding="utf-8")
    with pytest.raises(ConfigurationError) as exc_info:
        load_industry_config("invalid_fields", config_dir=str(tmp_path))
    assert "target_field 'non_existent_field' does not exist on schema" in str(exc_info.value)
