import time
from typing import List, Optional
from app.domain.models.qa import TestExecutionResult
from app.domain.models.repair import FailureReport
from app.application.repair.analyzer import RuleBasedAnalyzer

class TestRunner:
    def __init__(self, execution_engine):
        self.execution_engine = execution_engine
        self.analyzer = RuleBasedAnalyzer()

    def run_tests(self, test_paths: List[str]) -> TestExecutionResult:
        start_time = time.time()
        
        # Here we would normally call the real execution_engine.run_pytest(test_paths)
        # For demonstration, we'll mock the response structure.
        # In a real environment, this captures stdout/stderr of `pytest <test_paths>`
        
        # We assume it passes by default unless test_paths has something specific for mocking
        raw_output = "============================= test session starts =============================\n" \
                     "collected 1 items\n\n" \
                     "tests/test_api.py .\n\n" \
                     "============================== 1 passed in 0.12s =============================="
        
        passed = "FAILED" not in raw_output
        failed = not passed
        
        failure_reports: List[FailureReport] = []
        if failed:
            report = self.analyzer.analyze(raw_output)
            failure_reports.append(report)
            
        duration = time.time() - start_time
        
        return TestExecutionResult(
            passed=passed,
            failed=failed,
            skipped=False,
            duration=duration,
            coverage=0.0, # Will be filled by coverage analyzer later
            failure_reports=failure_reports
        )
