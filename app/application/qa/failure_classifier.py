from app.domain.models.qa import FailureClassification
from app.domain.models.repair import FailureReport

class FailureClassifier:
    def classify(self, report: FailureReport) -> FailureClassification:
        # A simple classifier to distinguish between application bugs, test bugs, environment issues
        if report.failure_type == "SyntaxError":
            # If the syntax error is in a test file, it's a test bug
            if any("test_" in f for f in report.affected_files):
                return FailureClassification.TEST
            return FailureClassification.APPLICATION
            
        elif report.failure_type == "ModuleNotFoundError":
            # Missing imports can be dependency or environment
            return FailureClassification.DEPENDENCY
            
        elif report.failure_type == "PytestFailure":
            # Usually means an assertion failed.
            # Could be a logic error (Application) or an invalid assumption (Test).
            # For this demo, we assume assertion failures are Application bugs.
            # A more sophisticated model would use an LLM here.
            return FailureClassification.APPLICATION
            
        return FailureClassification.UNKNOWN
