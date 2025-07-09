# Formulas: Excel to Python Converter

A tool for converting Excel formulas to executable Python code. This project provides both a web API and a command-line interface for converting Excel, CSV, or TSV files containing formulas into Python scripts.

## Features

- Convert Excel formulas to Python code
- Support for Excel (.xlsx), CSV, and TSV files
- Web API for integration with other applications
- Command-line interface for direct usage
- Sandbox execution environment for testing generated code
- Option to force runtime evaluation using xlcalculator

## Installation

### From PyPI (Recommended)

```bash
pip install formulas
```

### From Source

```bash
git clone https://github.com/yourusername/formulas.git
cd formulas
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Basic usage
formulas-cli input.xlsx

# Save output to a file
formulas-cli input.xlsx -o output.py

# Force runtime evaluation
formulas-cli input.xlsx --force-evaluator
```

### Web API

Start the server:

```bash
uvicorn src.main:app --reload
```

Then use the API:

- Upload a file to `http://localhost:8000/convert/` using a POST request
- Optionally specify `output_filename` and `force_evaluator` parameters

## API Documentation

When the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/formulas.git
cd formulas

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 