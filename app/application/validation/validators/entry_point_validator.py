from typing import Dict, Tuple, List
from .base_validator import BaseValidator

class EntryPointValidator(BaseValidator):
    """Validates that a main entry point like main.py or app.py exists."""
    
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        errors = []
        # Check for typical entry points
        entry_points = ["main.py", "app.py", "run.py"]
        if not any(ep in files for ep in entry_points):
            errors.append("No entry point found (expected main.py, app.py, or run.py).")
            
        return len(errors) == 0, errors
