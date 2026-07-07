from abc import ABC, abstractmethod
from typing import Dict, Tuple, List

class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    @abstractmethod
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate the generated files.
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        pass
