from typing import List, Type

import pandas as pd
from pydantic import BaseModel

from core.paths import resolve_project_path
from repositories.base_repository import BaseRepository, RepositoryError


class CSVRepository(BaseRepository):
    """Repository implementation that reads and validates data from a CSV file."""
    
    def __init__(self, file_path: str, record_class: Type[BaseModel]):
        """Initializes the repository with a specific CSV file and validation model."""
        self.file_path = resolve_project_path(file_path)
        self.record_class = record_class
        
    def load_records(self) -> List[BaseModel]:
        """Loads CSV rows, parsing and validating each against the configured Pydantic model.
        
        Raises RepositoryError on file, parsing, or validation failures.
        """
        try:
            # We explicitly use pandas to read the CSV
            df = pd.read_csv(self.file_path)
        except Exception as e:
            raise RepositoryError(f"Failed to read CSV file at '{self.file_path}': {e}")
            
        records = []
        for index, row in df.iterrows():
            try:
                # Convert series to dict. We replace NaN with None for Pydantic if needed
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                record = self.record_class(**row_dict)
                records.append(record)
            except Exception as e:
                raise RepositoryError(
                    f"Validation failed for row {index} in '{self.file_path}' using schema "
                    f"'{self.record_class.__name__}': {e}"
                )
                
        return records
