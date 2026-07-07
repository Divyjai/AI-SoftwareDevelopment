from typing import Dict, Tuple, List
from .base_validator import BaseValidator

class DependencyValidator(BaseValidator):
    """Validates that requirements.txt exists and is somewhat well-formed."""
    
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        errors = []
        if "requirements.txt" not in files:
            errors.append("Missing requirements.txt")
        else:
            lines = files["requirements.txt"].splitlines()
            if not any(lines):
                errors.append("requirements.txt is empty")
                
        return len(errors) == 0, errors
