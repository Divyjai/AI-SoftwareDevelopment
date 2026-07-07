import ast
from pathlib import Path
from app.domain.models.repair import Patch

class PatchValidator:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)

    def validate(self, patch: Patch) -> bool:
        file_path = self.workspace_path / patch.file
        if not file_path.exists():
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to simulate the patch application in-memory
        new_content = ""
        if patch.change_type == "REPLACE":
            if patch.old_fragment not in content:
                return False
            new_content = content.replace(patch.old_fragment, patch.new_fragment)
        elif patch.change_type == "DELETE":
            new_content = content.replace(patch.old_fragment, "")
        elif patch.change_type == "ADD":
            new_content = content + "\n" + patch.new_fragment
        else:
            return False

        # Validate syntax of the patched code
        try:
            ast.parse(new_content)
        except SyntaxError:
            return False

        return True
