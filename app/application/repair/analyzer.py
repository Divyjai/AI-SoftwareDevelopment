import re
from app.domain.models.repair import FailureReport

class RuleBasedAnalyzer:
    def analyze(self, raw_output: str) -> FailureReport:
        # A simple deterministic parser
        failure_type = "Unknown"
        root_cause = "Could not parse"
        affected_files = []
        is_deterministic = False

        if "SyntaxError" in raw_output:
            failure_type = "SyntaxError"
            match = re.search(r'File "(.*?)", line \d+', raw_output)
            if match:
                affected_files.append(match.group(1))
            root_cause = "Syntax error in the file"
            is_deterministic = True
        elif "ModuleNotFoundError" in raw_output:
            failure_type = "ModuleNotFoundError"
            match = re.search(r"No module named '(.*?)'", raw_output)
            if match:
                root_cause = f"Missing dependency: {match.group(1)}"
            is_deterministic = True
        elif "FAILED" in raw_output or "FAILURES" in raw_output:
            failure_type = "PytestFailure"
            root_cause = "Test assertion failed or raised an exception"
            match = re.search(r'(test_.*?\.py)', raw_output)
            if match:
                affected_files.append(match.group(1))
        else:
            # Fallback to general traceback
            matches = re.findall(r'File "(.*?)", line \d+', raw_output)
            if matches:
                affected_files.append(matches[-1])  # The last file is typically the throw site

        return FailureReport(
            failure_type=failure_type,
            root_cause=root_cause,
            severity="HIGH",
            affected_files=affected_files,
            affected_nodes=[],
            stack_trace=raw_output,
            suggested_strategy="Requires deeper analysis" if not is_deterministic else "Fix deterministic issue",
            confidence=1.0 if is_deterministic else 0.5,
            is_deterministic=is_deterministic
        )

class LLMEnricher:
    def enrich(self, report: FailureReport) -> FailureReport:
        # If we already deterministically parsed the error and it's a known syntax issue, skip LLM
        if report.is_deterministic:
            return report
        
        # Here we would call the LLM to explain the PytestFailure or Unknown error
        # In this mock, we just add a suggested strategy based on the trace
        if report.failure_type == "PytestFailure":
            report.suggested_strategy = "Inspect the failed test assertion and the corresponding endpoint."
            report.confidence = 0.8
        elif len(report.affected_files) > 0:
            report.suggested_strategy = "Extracted file from traceback, analyze the target function."
            report.confidence = 0.7
        
        return report
