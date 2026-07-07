import os
from pathlib import Path
from app.domain.models.repair import Patch

class PatchApplier:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)

    def apply(self, patch: Patch) -> bool:
        file_path = self.workspace_path / patch.file
        if not file_path.exists():
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if patch.change_type == "REPLACE":
            if patch.old_fragment not in content:
                # Naive check failed, we might need a more resilient replace
                return False
            new_content = content.replace(patch.old_fragment, patch.new_fragment)
        elif patch.change_type == "DELETE":
            new_content = content.replace(patch.old_fragment, "")
        elif patch.change_type == "ADD":
            # Very naive append to the end if target_node is a file
            new_content = content + "\n" + patch.new_fragment
        else:
            return False

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True
