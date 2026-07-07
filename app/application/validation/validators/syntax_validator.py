import ast
from typing import Dict, Tuple, List
from .base_validator import BaseValidator

class SyntaxValidator(BaseValidator):
    """Validates Python syntax for generated files."""
    
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        errors = []
        for filename, content in files.items():
            if filename.endswith(".py"):
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"Syntax error in {filename}: {str(e)}")
        
        return len(errors) == 0, errors
