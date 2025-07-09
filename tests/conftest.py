import pytest
import tempfile
import os
from unittest.mock import MagicMock
from xlcalculator.model import Model

@pytest.fixture
def sample_excel_content():
    """Provide sample Excel file content for testing."""
    return b"mock excel file content"

@pytest.fixture
def mock_model():
    """Create a mock xlcalculator Model for testing."""
    model = MagicMock(spec=Model)
    
    # Create mock cells with formulas and values
    cell_a1 = MagicMock()
    cell_a1.formula = None  # Input cell
    cell_a1.formula_address = "Sheet1!A1"
    cell_a1.value = 5
    cell_a1.precedents = []
    
    cell_b1 = MagicMock()
    cell_b1.formula = "A1*2"
    cell_b1.formula_address = "Sheet1!B1"
    cell_b1.value = 10
    precedent_a1 = MagicMock()
    precedent_a1.formula_address = "Sheet1!A1"
    cell_b1.precedents = [precedent_a1]
    
    cell_c1 = MagicMock()
    cell_c1.formula = "SUM(A1:B1)"
    cell_c1.formula_address = "Sheet1!C1"
    cell_c1.value = 15
    precedent_a1_for_c1 = MagicMock()
    precedent_a1_for_c1.formula_address = "Sheet1!A1"
    precedent_b1 = MagicMock()
    precedent_b1.formula_address = "Sheet1!B1"
    cell_c1.precedents = [precedent_a1_for_c1, precedent_b1]
    
    # Set up the model.cells dictionary
    model.cells = {
        "Sheet1!A1": cell_a1,
        "Sheet1!B1": cell_b1,
        "Sheet1!C1": cell_c1
    }
    
    return model

@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    
    # Clean up after the test
    if os.path.exists(tmp.name):
        os.remove(tmp.name) 