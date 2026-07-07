import pytest
from app.application.qa.failure_classifier import FailureClassifier
from app.domain.models.qa import FailureClassification
from app.domain.models.repair import FailureReport

def test_syntax_error_in_test_file():
    classifier = FailureClassifier()
    report = FailureReport(
        failure_type="SyntaxError",
        root_cause="Syntax Error",
        severity="HIGH",
        affected_files=["tests/test_api.py"],
        affected_nodes=[],
        stack_trace="",
        suggested_strategy="",
        confidence=1.0,
        is_deterministic=True
    )
    assert classifier.classify(report) == FailureClassification.TEST

def test_syntax_error_in_app_file():
    classifier = FailureClassifier()
    report = FailureReport(
        failure_type="SyntaxError",
        root_cause="Syntax Error",
        severity="HIGH",
        affected_files=["app/api.py"],
        affected_nodes=[],
        stack_trace="",
        suggested_strategy="",
        confidence=1.0,
        is_deterministic=True
    )
    assert classifier.classify(report) == FailureClassification.APPLICATION

def test_module_not_found():
    classifier = FailureClassifier()
    report = FailureReport(
        failure_type="ModuleNotFoundError",
        root_cause="Missing requests",
        severity="HIGH",
        affected_files=["app/api.py"],
        affected_nodes=[],
        stack_trace="",
        suggested_strategy="",
        confidence=1.0,
        is_deterministic=True
    )
    assert classifier.classify(report) == FailureClassification.DEPENDENCY

def test_pytest_assertion_failure():
    classifier = FailureClassifier()
    report = FailureReport(
        failure_type="PytestFailure",
        root_cause="AssertionError",
        severity="HIGH",
        affected_files=["tests/test_api.py"],
        affected_nodes=[],
        stack_trace="",
        suggested_strategy="",
        confidence=1.0,
        is_deterministic=True
    )
    assert classifier.classify(report) == FailureClassification.APPLICATION
