from dataclasses import dataclass, field
from typing import List

@dataclass
class SecurityPolicy:
    max_execution_time_seconds: int = 30
    max_output_size_bytes: int = 1048576 # 1MB
    max_file_count: int = 1000
    blocked_env_vars: List[str] = field(default_factory=lambda: ["AWS_ACCESS_KEY_ID", "GITHUB_TOKEN"])
