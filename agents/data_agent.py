from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState
from repositories.csv_repository import CSVRepository
from services.config_loader import load_industry_config
from services.schema_registry import SchemaRegistry


class DataAgent(BaseAgent):
    """Data Agent: Automatically loads data from the configured industry CSV file using the registered schema."""
    
    @property
    def name(self) -> str:
        return "DataAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Load the configuration to determine data path
        config = load_industry_config(state.industry)
        
        if not config.record_schema:
            raise ValueError(f"No record schema configured for industry '{state.industry}'")
            
        # Resolve record model structure from registry
        record_class = SchemaRegistry.get_schema(config.record_schema)
            
        # Instantiate repository and load records
        repo = CSVRepository(config.dataset_reference, record_class)
        records = repo.load_records()
        
        state.retrieved_data = records
        return state
