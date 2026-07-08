from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FrontendMetrics:
    generated_pages: int = 0
    generated_components: int = 0
    build_time_ms: Optional[int] = None
    bundle_size_kb: Optional[float] = None
    accessibility_score: Optional[int] = None
    performance_score: Optional[int] = None
    responsive_score: Optional[int] = None
    test_coverage_percent: Optional[float] = None
    hydration_errors: int = 0
    repair_count: int = 0
