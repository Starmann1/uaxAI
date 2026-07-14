from pathlib import Path

import yaml

from core.paths import CONFIG_DIRECTORY
from models.config_models import IndustryConfig


class ConfigurationError(Exception):
    """Exception raised when loading or validating configuration fails."""
    pass

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
        return IndustryConfig(**raw_data)
    except Exception as e:
        raise ConfigurationError(f"Failed to validate configuration for industry '{industry_key}': {e}")
