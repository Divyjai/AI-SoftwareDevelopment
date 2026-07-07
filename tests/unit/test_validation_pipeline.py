import pytest
from app.application.validation.pipeline import ValidationPipeline

def test_validation_pipeline_success():
    files = {
        "main.py": "def main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()",
        "requirements.txt": "fastapi\nuvicorn"
    }
    pipeline = ValidationPipeline()
    is_valid, errors = pipeline.validate(files)
    assert is_valid is True
    assert len(errors) == 0

def test_validation_pipeline_syntax_error():
    files = {
        "main.py": "def main()  # Missing colon\n    print('Hello')",
        "requirements.txt": "fastapi\nuvicorn"
    }
    pipeline = ValidationPipeline()
    is_valid, errors = pipeline.validate(files)
    assert is_valid is False
    assert len(errors) > 0
    assert any("Syntax error" in err for err in errors)

def test_validation_pipeline_missing_entry_point():
    files = {
        "utils.py": "def add(a, b):\n    return a + b",
        "requirements.txt": "fastapi"
    }
    pipeline = ValidationPipeline()
    is_valid, errors = pipeline.validate(files)
    assert is_valid is False
    assert any("No entry point found" in err for err in errors)

def test_validation_pipeline_missing_dependencies():
    files = {
        "main.py": "print('hello')"
    }
    pipeline = ValidationPipeline()
    is_valid, errors = pipeline.validate(files)
    assert is_valid is False
    assert any("Missing requirements.txt" in err for err in errors)
