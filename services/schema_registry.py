from typing import Dict, Type

from pydantic import BaseModel

from models.data_models import BatchRecord, ProductionRecord


class SchemaRegistryError(Exception):
    """Exception raised when schema resolution fails."""
    pass


class SchemaRegistry:
    """Registry mapping string schema keys to Pydantic models."""
    
    _registry: Dict[str, Type[BaseModel]] = {
        "pharmaceutical_batch": BatchRecord,
        "automotive_production": ProductionRecord,
    }
    
    @classmethod
    def get_schema(cls, schema_name: str) -> Type[BaseModel]:
        """Resolves a record model by schema name. Raises SchemaRegistryError if not found."""
        if not schema_name:
            raise SchemaRegistryError("Schema name cannot be empty.")
        if schema_name not in cls._registry:
            raise SchemaRegistryError(f"Unknown record schema identifier: '{schema_name}'")
        return cls._registry[schema_name]
        
    @classmethod
    def register_schema(cls, schema_name: str, model_cls: Type[BaseModel]) -> None:
        """Dynamically registers a new schema mapping."""
        cls._registry[schema_name] = model_cls
