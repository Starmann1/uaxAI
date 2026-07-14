from pathlib import Path
from typing import List

import yaml

from core.paths import CONFIG_DIRECTORY, resolve_project_path
from models.config_models import IndustryConfig
from services.schema_registry import SchemaRegistry, SchemaRegistryError


class ConfigurationError(Exception):
    """Exception raised when loading or validating configuration fails."""
    pass


def list_industries(config_dir: str | Path | None = None) -> List[str]:
    """Scans the configuration directory and lists all available industry keys."""
    base_directory = Path(config_dir) if config_dir is not None else CONFIG_DIRECTORY
    if not base_directory.exists():
        return []
    return [p.stem for p in base_directory.glob("*.yaml")]


def load_industry_config(
    industry_key: str, config_dir: str | Path | None = None
) -> IndustryConfig:
    """Loads a configuration for a specific industry by key from YAML and validates it.
    
    Raises ConfigurationError on any parsing, loading, or validation failures.
    """
    base_directory = Path(config_dir) if config_dir is not None else CONFIG_DIRECTORY
    config_path = base_directory / f"{industry_key}.yaml"
    
    if not config_path.exists():
        raise ConfigurationError(f"Configuration file not found for industry '{industry_key}': {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to parse YAML file for industry '{industry_key}': {e}")
        
    if not isinstance(raw_data, dict):
        raise ConfigurationError(f"Configuration YAML for '{industry_key}' must evaluate to a dictionary.")
        
    try:
        config = IndustryConfig(**raw_data)
    except Exception as e:
        raise ConfigurationError(f"Failed to validate configuration for industry '{industry_key}': {e}")
        
    # Check dataset existence
    dataset_path = resolve_project_path(config.dataset_reference)
    if not dataset_path.exists():
        raise ConfigurationError(f"Dataset file reference does not exist: {dataset_path}")
        
    # Validate record schema key if provided
    record_model = None
    if config.record_schema:
        try:
            record_model = SchemaRegistry.get_schema(config.record_schema)
        except SchemaRegistryError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")
            
    # Validate duplicate metric IDs and field names against resolved schema
    metric_ids = set()
    for m in config.metrics:
        if m.metric_id in metric_ids:
            raise ConfigurationError(f"Duplicate metric ID found in configuration: '{m.metric_id}'")
        metric_ids.add(m.metric_id)
        
        # Validate aggregation fields exist on schema
        if record_model:
            if m.target_field and m.target_field not in record_model.model_fields:
                raise ConfigurationError(
                    f"Metric '{m.metric_id}' target_field '{m.target_field}' does not exist on schema '{config.record_schema}'"
                )
            if m.filter_field and m.filter_field not in record_model.model_fields:
                raise ConfigurationError(
                    f"Metric '{m.metric_id}' filter_field '{m.filter_field}' does not exist on schema '{config.record_schema}'"
                )
                
    return config
