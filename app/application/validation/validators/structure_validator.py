from typing import Dict, Tuple, List
from .base_validator import BaseValidator

class StructureValidator(BaseValidator):
    """Validates that necessary basic structure exists in generated files."""
    
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        errors = []
        if not files:
            errors.append("No files were generated.")
            return False, errors
            
        return len(errors) == 0, errors
