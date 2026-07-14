from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel


class RepositoryError(Exception):
    """Custom exception raised by the repository layer."""
    pass

class BaseRepository(ABC):
    """Abstract base class representing the data repository layer."""
    
    @abstractmethod
    def load_records(self) -> List[BaseModel]:
        """Loads and returns all records from the storage system.
        
        Raises RepositoryError on failure.
        """
        pass
