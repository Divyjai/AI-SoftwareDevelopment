import ast
from typing import Dict, Tuple

class CodeValidator:
    def validate(self, files: Dict[str, str]) -> Tuple[bool, str]:
        for filename, content in files.items():
            if filename.endswith(".py"):
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    return False, f"Syntax error in {filename}: {str(e)}"
        return True, "Valid"
