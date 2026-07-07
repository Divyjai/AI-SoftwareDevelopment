import pytest
from app.application.repair.analyzer import RuleBasedAnalyzer

def test_syntax_error_parsing():
    analyzer = RuleBasedAnalyzer()
    raw_error = '''Traceback (most recent call last):
  File "app/api.py", line 15
    def get_user()
                 ^
SyntaxError: expected ':'
'''
    report = analyzer.analyze(raw_error)
    assert report.failure_type == "SyntaxError"
    assert report.is_deterministic == True
    assert "app/api.py" in report.affected_files

def test_module_not_found_parsing():
    analyzer = RuleBasedAnalyzer()
    raw_error = '''Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import some_missing_module
ModuleNotFoundError: No module named 'some_missing_module'
'''
    report = analyzer.analyze(raw_error)
    assert report.failure_type == "ModuleNotFoundError"
    assert report.is_deterministic == True
    assert "Missing dependency: some_missing_module" in report.root_cause

def test_pytest_failure_parsing():
    analyzer = RuleBasedAnalyzer()
    raw_error = '''=================================== FAILURES ===================================
_________________________________ test_get_user ________________________________

    def test_get_user():
>       assert get_user() == "Test"
E       AssertionError: assert 'Wrong' == 'Test'

tests/test_api.py:5: AssertionError
'''
    report = analyzer.analyze(raw_error)
    assert report.failure_type == "PytestFailure"
    assert "test_api.py" in report.affected_files
