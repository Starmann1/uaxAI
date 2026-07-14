from agents.base_agent import BaseAgent
from models.data_models import BatchRecord, ProductionRecord
from models.workflow_state import WorkflowState
from repositories.csv_repository import CSVRepository
from services.config_loader import load_industry_config


class DataAgent(BaseAgent):
    """Data Agent: Automatically loads data from the configured industry CSV file."""
    
    @property
    def name(self) -> str:
        return "DataAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Load the configuration to determine data path
        config = load_industry_config(state.industry)
        
        # Decide record model structure based on industry
        if state.industry == "automotive":
            record_class = ProductionRecord
        elif state.industry == "pharma":
            record_class = BatchRecord
        else:
            raise ValueError(f"Unknown industry for data repository loading: '{state.industry}'")
            
        # Instantiate repository and load records
        repo = CSVRepository(config.dataset_reference, record_class)
        records = repo.load_records()
        
        state.retrieved_data = records
        return state
