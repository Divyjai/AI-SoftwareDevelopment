from typing import Dict, Tuple, List
from .validators.base_validator import BaseValidator
from .validators.syntax_validator import SyntaxValidator
from .validators.structure_validator import StructureValidator
from .validators.dependency_validator import DependencyValidator
from .validators.entry_point_validator import EntryPointValidator

class ValidationPipeline:
    """Orchestrates a series of validators over generated files."""
    
    def __init__(self, validators: List[BaseValidator] = None):
        if validators is None:
            self.validators = [
                SyntaxValidator(),
                StructureValidator(),
                DependencyValidator(),
                EntryPointValidator()
            ]
        else:
            self.validators = validators
            
    def validate(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        all_errors = []
        is_valid = True
        
        for validator in self.validators:
            valid, errors = validator.validate(files)
            if not valid:
                is_valid = False
                all_errors.extend(errors)
                
        return is_valid, all_errors
