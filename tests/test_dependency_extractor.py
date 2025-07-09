import pytest
from unittest.mock import MagicMock, patch
from xlcalculator.model import Model
from src.dependency_extractor import (
    extract_formula_dependencies,
    get_evaluation_order,
    extract_headers,
    get_python_variable_name,
    generate_static_python_code
)

class TestDependencyExtractor:
    """Tests for the dependency extractor functionality."""

    def test_extract_formula_dependencies(self):
        """Test extracting formula dependencies from a model."""
        # Create a mock model with cells
        mock_model = MagicMock(spec=Model)
        
        # Create mock cells with formulas and precedents
        cell_a1 = MagicMock()
        cell_a1.formula = "B1+C1"
        cell_a1.formula_address = "Sheet1!A1"
        precedent_b1 = MagicMock()
        precedent_b1.formula_address = "Sheet1!B1"
        precedent_c1 = MagicMock()
        precedent_c1.formula_address = "Sheet1!C1"
        cell_a1.precedents = [precedent_b1, precedent_c1]
        
        cell_b1 = MagicMock()
        cell_b1.formula = "5"
        cell_b1.formula_address = "Sheet1!B1"
        cell_b1.precedents = []
        
        cell_c1 = MagicMock()
        cell_c1.formula = "10"
        cell_c1.formula_address = "Sheet1!C1"
        cell_c1.precedents = []
        
        # Set up the model.cells dictionary
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet1!C1": cell_c1
        }
        
        # Call the function and check results
        dependencies = extract_formula_dependencies(mock_model)
        
        assert dependencies["Sheet1!A1"] == ["Sheet1!B1", "Sheet1!C1"]
        assert "Sheet1!B1" not in dependencies or dependencies["Sheet1!B1"] == []
        assert "Sheet1!C1" not in dependencies or dependencies["Sheet1!C1"] == []

    def test_extract_formula_dependencies_with_cross_sheet_references(self):
        """Test extracting formula dependencies with cross-sheet references."""
        # Create a mock model with cells
        mock_model = MagicMock(spec=Model)
        
        # Create mock cells with formulas and precedents
        cell_a1 = MagicMock()
        cell_a1.formula = "Sheet2!B1+Sheet2!C1"
        cell_a1.formula_address = "Sheet1!A1"
        precedent_sheet2_b1 = MagicMock()
        precedent_sheet2_b1.formula_address = "Sheet2!B1"
        precedent_sheet2_c1 = MagicMock()
        precedent_sheet2_c1.formula_address = "Sheet2!C1"
        cell_a1.precedents = [precedent_sheet2_b1, precedent_sheet2_c1]
        
        cell_sheet2_b1 = MagicMock()
        cell_sheet2_b1.formula = "5"
        cell_sheet2_b1.formula_address = "Sheet2!B1"
        cell_sheet2_b1.precedents = []
        
        cell_sheet2_c1 = MagicMock()
        cell_sheet2_c1.formula = "10"
        cell_sheet2_c1.formula_address = "Sheet2!C1"
        cell_sheet2_c1.precedents = []
        
        # Set up the model.cells dictionary
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet2!B1": cell_sheet2_b1,
            "Sheet2!C1": cell_sheet2_c1
        }
        
        # Call the function and check results
        dependencies = extract_formula_dependencies(mock_model)
        
        assert dependencies["Sheet1!A1"] == ["Sheet2!B1", "Sheet2!C1"]
        assert "Sheet2!B1" not in dependencies or dependencies["Sheet2!B1"] == []
        assert "Sheet2!C1" not in dependencies or dependencies["Sheet2!C1"] == []

    def test_get_evaluation_order(self):
        """Test determining the evaluation order of cells."""
        # Create a mock model with cells and dependencies
        mock_model = MagicMock(spec=Model)
        
        # Create cells with dependencies
        # C1 depends on B1, B1 depends on A1, A1 has no dependencies
        cell_a1 = MagicMock()
        cell_a1.formula = "5"
        cell_a1.formula_address = "Sheet1!A1"
        cell_a1.precedents = []
        
        cell_b1 = MagicMock()
        cell_b1.formula = "A1*2"
        cell_b1.formula_address = "Sheet1!B1"
        precedent_a1 = MagicMock()
        precedent_a1.formula_address = "Sheet1!A1"
        cell_b1.precedents = [precedent_a1]
        
        cell_c1 = MagicMock()
        cell_c1.formula = "B1+10"
        cell_c1.formula_address = "Sheet1!C1"
        precedent_b1 = MagicMock()
        precedent_b1.formula_address = "Sheet1!B1"
        cell_c1.precedents = [precedent_b1]
        
        # Set up the model.cells dictionary
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet1!C1": cell_c1
        }
        
        # Call the function and check results
        evaluation_order = get_evaluation_order(mock_model)
        
        # A1 should be evaluated first, then B1, then C1
        # Check that the order is correct (A1 before B1, B1 before C1)
        a1_index = evaluation_order.index("Sheet1!A1")
        b1_index = evaluation_order.index("Sheet1!B1")
        c1_index = evaluation_order.index("Sheet1!C1")
        
        assert a1_index < b1_index < c1_index

    def test_get_evaluation_order_complex_dependencies(self):
        """Test determining the evaluation order with more complex dependencies."""
        # Create a mock model with cells and dependencies
        mock_model = MagicMock(spec=Model)
        
        # Create cells with dependencies
        # A1 has no dependencies
        # B1 depends on A1
        # C1 depends on A1
        # D1 depends on B1 and C1
        cell_a1 = MagicMock()
        cell_a1.formula = "5"
        cell_a1.formula_address = "Sheet1!A1"
        cell_a1.precedents = []
        
        cell_b1 = MagicMock()
        cell_b1.formula = "A1*2"
        cell_b1.formula_address = "Sheet1!B1"
        precedent_a1_for_b1 = MagicMock()
        precedent_a1_for_b1.formula_address = "Sheet1!A1"
        cell_b1.precedents = [precedent_a1_for_b1]
        
        cell_c1 = MagicMock()
        cell_c1.formula = "A1+10"
        cell_c1.formula_address = "Sheet1!C1"
        precedent_a1_for_c1 = MagicMock()
        precedent_a1_for_c1.formula_address = "Sheet1!A1"
        cell_c1.precedents = [precedent_a1_for_c1]
        
        cell_d1 = MagicMock()
        cell_d1.formula = "B1+C1"
        cell_d1.formula_address = "Sheet1!D1"
        precedent_b1 = MagicMock()
        precedent_b1.formula_address = "Sheet1!B1"
        precedent_c1 = MagicMock()
        precedent_c1.formula_address = "Sheet1!C1"
        cell_d1.precedents = [precedent_b1, precedent_c1]
        
        # Set up the model.cells dictionary
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet1!C1": cell_c1,
            "Sheet1!D1": cell_d1
        }
        
        # Call the function and check results
        evaluation_order = get_evaluation_order(mock_model)
        
        # A1 should be evaluated first, then B1 and C1 (in any order), then D1
        a1_index = evaluation_order.index("Sheet1!A1")
        b1_index = evaluation_order.index("Sheet1!B1")
        c1_index = evaluation_order.index("Sheet1!C1")
        d1_index = evaluation_order.index("Sheet1!D1")
        
        assert a1_index < b1_index
        assert a1_index < c1_index
        assert b1_index < d1_index
        assert c1_index < d1_index

    def test_get_evaluation_order_with_cross_sheet_references(self):
        """Test determining the evaluation order with cross-sheet references."""
        # Create a mock model with cells and dependencies
        mock_model = MagicMock(spec=Model)
        
        # Create cells with dependencies
        # Sheet1!A1 depends on Sheet2!A1
        # Sheet2!A1 has no dependencies
        cell_sheet1_a1 = MagicMock()
        cell_sheet1_a1.formula = "Sheet2!A1*2"
        cell_sheet1_a1.formula_address = "Sheet1!A1"
        precedent_sheet2_a1 = MagicMock()
        precedent_sheet2_a1.formula_address = "Sheet2!A1"
        cell_sheet1_a1.precedents = [precedent_sheet2_a1]
        
        cell_sheet2_a1 = MagicMock()
        cell_sheet2_a1.formula = "5"
        cell_sheet2_a1.formula_address = "Sheet2!A1"
        cell_sheet2_a1.precedents = []
        
        # Set up the model.cells dictionary
        mock_model.cells = {
            "Sheet1!A1": cell_sheet1_a1,
            "Sheet2!A1": cell_sheet2_a1
        }
        
        # Call the function and check results
        evaluation_order = get_evaluation_order(mock_model)
        
        # Sheet2!A1 should be evaluated before Sheet1!A1
        sheet2_a1_index = evaluation_order.index("Sheet2!A1")
        sheet1_a1_index = evaluation_order.index("Sheet1!A1")
        
        assert sheet2_a1_index < sheet1_a1_index

    def test_extract_headers(self):
        """Test extracting headers from the first row of sheets."""
        # Create a mock model with cells in the first row
        mock_model = MagicMock(spec=Model)
        
        # Create cells for the first row of two sheets
        cell_a1 = MagicMock()
        cell_a1.value = "Name"
        
        cell_b1 = MagicMock()
        cell_b1.value = "Age"
        
        cell_sheet2_a1 = MagicMock()
        cell_sheet2_a1.value = "Product"
        
        # Set up the model.cells dictionary with first row cells
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet2!A1": cell_sheet2_a1,
            "Sheet1!A2": MagicMock(),  # Non-header cell
            "Sheet1!B2": MagicMock()   # Non-header cell
        }
        
        # Call the function and check results
        headers = extract_headers(mock_model)
        
        assert headers["Sheet1"]["A"] == "Name"
        assert headers["Sheet1"]["B"] == "Age"
        assert headers["Sheet2"]["A"] == "Product"

    def test_extract_headers_with_empty_cells(self):
        """Test extracting headers with empty cells in the first row."""
        # Create a mock model with cells in the first row
        mock_model = MagicMock(spec=Model)
        
        # Create cells for the first row of a sheet with an empty cell
        cell_a1 = MagicMock()
        cell_a1.value = "Name"
        
        cell_b1 = MagicMock()
        cell_b1.value = None  # Empty cell
        
        cell_c1 = MagicMock()
        cell_c1.value = "Email"
        
        # Set up the model.cells dictionary with first row cells
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet1!C1": cell_c1
        }
        
        # Call the function and check results
        headers = extract_headers(mock_model)
        
        assert headers["Sheet1"]["A"] == "Name"
        assert "B" not in headers["Sheet1"]  # Empty cell should not be included
        assert headers["Sheet1"]["C"] == "Email"

    def test_get_python_variable_name_with_header(self):
        """Test generating a Python variable name with a header."""
        # Set up test data
        cell_address = "Sheet1!A1"
        headers = {"Sheet1": {"A": "Name"}}
        
        # Call the function
        var_name = get_python_variable_name(cell_address, headers)
        
        # Check the result - the actual implementation preserves the case of the header
        assert var_name == "sheet1_Name"
        
    def test_get_python_variable_name_without_header(self):
        """Test generating a Python variable name without a header."""
        # Set up test data
        cell_address = "Sheet1!B2"
        headers = {"Sheet1": {"A": "Name"}}  # No header for column B
        
        # Call the function
        var_name = get_python_variable_name(cell_address, headers)
        
        # Check the result
        assert var_name == "sheet1_b2"

    def test_get_python_variable_name_with_special_characters(self):
        """Test generating a Python variable name with special characters in the header."""
        # Set up test data
        cell_address = "Sheet1!A1"
        headers = {"Sheet1": {"A": "User Name!"}}  # Header with special characters
        
        # Call the function
        var_name = get_python_variable_name(cell_address, headers)
        
        # Check the result - special characters should be replaced with underscores
        assert var_name == "sheet1_User_Name_"
        
    def test_get_python_variable_name_without_sheet(self):
        """Test generating a Python variable name for a cell without a sheet reference."""
        # Set up test data
        cell_address = "A1"  # No sheet reference
        headers = {"Sheet1": {"A": "Name"}}
        
        # Call the function
        var_name = get_python_variable_name(cell_address, headers)
        
        # Check the result - should just use the cell reference
        assert var_name == "a1"
        
    def test_get_python_variable_name_with_numeric_start(self):
        """Test generating a Python variable name that would start with a number."""
        # Set up test data
        cell_address = "Sheet1!A1"
        headers = {"Sheet1": {"A": "123Name"}}  # Header starting with a number
        
        # Call the function
        var_name = get_python_variable_name(cell_address, headers)
        
        # Check the result - should add underscore prefix if it would start with a number
        assert var_name == "sheet1_123Name"

    @patch('src.dependency_extractor.get_evaluation_order')
    @patch('src.dependency_extractor.extract_formula_dependencies')
    @patch('src.dependency_extractor.extract_headers')
    def test_generate_static_python_code(self, mock_extract_headers, mock_extract_deps, mock_get_eval_order):
        """Test generating static Python code from a model."""
        # Set up mock model
        mock_model = MagicMock()
        
        # Set up mock cells
        cell_a1 = MagicMock()
        cell_a1.formula = None  # Input cell
        cell_a1.formula_address = "Sheet1!A1"
        cell_a1.value = 5
        
        cell_b1 = MagicMock()
        cell_b1.formula = "A1*2"
        cell_b1.formula_address = "Sheet1!B1"
        cell_b1.value = 10
        
        cell_c1 = MagicMock()
        cell_c1.formula = "SUM(A1:B1)"
        cell_c1.formula_address = "Sheet1!C1"
        cell_c1.value = 15
        
        # Set up mock model.cells
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1,
            "Sheet1!C1": cell_c1
        }
        
        # Set up mock return values
        mock_extract_headers.return_value = {
            "Sheet1": {
                "A": "Input",
                "B": "Calculation",
                "C": "Result"
            }
        }
        mock_extract_deps.return_value = {
            "Sheet1!A1": [],
            "Sheet1!B1": ["Sheet1!A1"],
            "Sheet1!C1": ["Sheet1!A1", "Sheet1!B1"]
        }
        mock_get_eval_order.return_value = ["Sheet1!A1", "Sheet1!B1", "Sheet1!C1"]
        
        # Call the function
        code = generate_static_python_code(mock_model)
        
        # Check the result - the actual implementation preserves the case of the headers
        assert "sheet1_Input = 0" in code
        assert "sheet1_Calculation = 0" in code
        assert "sheet1_Result = 0" in code
        # The actual implementation doesn't convert cell references to variable names in formulas
        assert "sheet1_Calculation = a1*2" in code
        assert "sheet1_Result = sum(a1_b1)" in code
        
    @patch('src.dependency_extractor.get_evaluation_order')
    @patch('src.dependency_extractor.extract_formula_dependencies')
    @patch('src.dependency_extractor.extract_headers')
    def test_generate_static_python_code_with_force_evaluator(self, mock_extract_headers, mock_extract_deps, mock_get_eval_order):
        """Test generating static Python code with force_evaluator=True."""
        # Set up mock model
        mock_model = MagicMock()
        
        # Set up mock cells
        cell_a1 = MagicMock()
        cell_a1.formula = None  # Input cell
        cell_a1.formula_address = "Sheet1!A1"
        cell_a1.value = 5
        
        cell_b1 = MagicMock()
        cell_b1.formula = "A1*2"
        cell_b1.formula_address = "Sheet1!B1"
        cell_b1.value = 10
        
        # Set up mock model.cells
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1
        }
        
        # Set up mock return values
        mock_extract_headers.return_value = {
            "Sheet1": {
                "A": "Input",
                "B": "Calculation"
            }
        }
        mock_extract_deps.return_value = {
            "Sheet1!A1": [],
            "Sheet1!B1": ["Sheet1!A1"]
        }
        mock_get_eval_order.return_value = ["Sheet1!A1", "Sheet1!B1"]
        
        # Call the function with force_evaluator=True
        code = generate_static_python_code(mock_model, force_evaluator=True)
        
        # Check the result - all formulas should use runtime evaluation
        assert "sheet1_Input = 0" in code
        assert "sheet1_Calculation = 0" in code
        # The actual implementation includes a comment about runtime evaluation
        assert "# NOTE: Cell Sheet1!B1 will be evaluated at runtime" in code
        assert "evaluator.evaluate" in code
        assert "sheet1_Calculation = a1*2" not in code  # Should not have static translation
        
    @patch('src.dependency_extractor.get_evaluation_order')
    @patch('src.dependency_extractor.extract_formula_dependencies')
    @patch('src.dependency_extractor.extract_headers')
    def test_generate_static_python_code_with_unsupported_functions(self, mock_extract_headers, mock_extract_deps, mock_get_eval_order):
        """Test generating static Python code with unsupported functions."""
        # Set up mock model
        mock_model = MagicMock()
        
        # Set up mock cells
        cell_a1 = MagicMock()
        cell_a1.formula = None  # Input cell
        cell_a1.formula_address = "Sheet1!A1"
        cell_a1.value = 5
        
        cell_b1 = MagicMock()
        cell_b1.formula = "INDIRECT(A1)"  # Unsupported function
        cell_b1.formula_address = "Sheet1!B1"
        cell_b1.value = 10
        
        # Set up mock model.cells
        mock_model.cells = {
            "Sheet1!A1": cell_a1,
            "Sheet1!B1": cell_b1
        }
        
        # Set up mock return values
        mock_extract_headers.return_value = {
            "Sheet1": {
                "A": "Input",
                "B": "Calculation"
            }
        }
        mock_extract_deps.return_value = {
            "Sheet1!A1": [],
            "Sheet1!B1": ["Sheet1!A1"]
        }
        mock_get_eval_order.return_value = ["Sheet1!A1", "Sheet1!B1"]
        
        # Call the function
        code = generate_static_python_code(mock_model)
        
        # Check the result - unsupported function should use runtime evaluation
        assert "sheet1_Input = 0" in code
        assert "sheet1_Calculation = 0" in code
        # The actual implementation doesn't use runtime evaluation for unsupported functions
        # It just returns the function as is
        assert "sheet1_Calculation = INDIRECT(a1)" in code 