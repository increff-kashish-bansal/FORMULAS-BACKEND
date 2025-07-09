# Excel to Python Formula Converter Tests

This directory contains tests for the Excel to Python formula converter application.

## Test Structure

The tests are organized as follows:

- **Unit Tests**: Test individual components in isolation
  - `test_file_handler.py`: Tests for file validation and handling
  - `test_formula_translator.py`: Tests for formula tokenization and translation
  - `test_dependency_extractor.py`: Tests for dependency extraction and evaluation order
  - `test_sandbox.py`: Tests for the sandboxed execution environment
  - `test_main.py`: Tests for the API endpoints
  - `test_cli.py`: Tests for the command-line interface

- **Integration Tests**: Test the end-to-end workflow
  - `test_integration.py`: Tests the complete workflow from file input to code generation and execution

- **Common Test Fixtures**:
  - `conftest.py`: Contains shared fixtures used across multiple test files

## Running Tests

### Prerequisites

Make sure you have the necessary dependencies installed:

```bash
pip install pytest pytest-asyncio
```

### Running All Tests

To run all tests:

```bash
pytest
```

### Running Specific Test Files

To run a specific test file:

```bash
pytest tests/test_file_handler.py
```

### Running Tests with Specific Markers

Some tests are marked as integration tests, which may require additional setup or take longer to run:

```bash
# Run only unit tests (excluding integration tests)
pytest -k "not integration"

# Run only integration tests
pytest -m integration
```

### Test Coverage

To check test coverage:

```bash
pip install pytest-cov
pytest --cov=src tests/
```

## Writing New Tests

When adding new functionality to the application, please also add corresponding tests:

1. For new components, create a new test file following the naming convention `test_*.py`
2. Use appropriate fixtures from `conftest.py` when possible
3. Mock external dependencies to ensure tests are isolated
4. For integration tests, use the `@pytest.mark.integration` decorator 