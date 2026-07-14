import pytest

from services.config_loader import ConfigurationError, load_industry_config


def test_load_valid_configs():
    # Test valid automotive config
    auto_cfg = load_industry_config("automotive")
    assert auto_cfg.industry_name == "automotive"
    assert "Overall Equipment Effectiveness (OEE)" in auto_cfg.terminology
    assert auto_cfg.metric == "Overall Equipment Effectiveness (OEE)"
    assert auto_cfg.dataset_reference == "data/automotive/production.csv"
    
    # Test valid pharma config
    pharma_cfg = load_industry_config("pharma")
    assert pharma_cfg.industry_name == "pharma"
    assert "Batch Yield Percentage" in pharma_cfg.terminology
    assert pharma_cfg.metric == "Batch Yield Percentage"
    assert pharma_cfg.dataset_reference == "data/pharma/batches.csv"

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
