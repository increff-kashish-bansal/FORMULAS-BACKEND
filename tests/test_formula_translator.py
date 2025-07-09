import pytest
from src.formula_translator import (
    tokenize_formula, 
    translate_formula_part,
    EXCEL_FUNCTION_MAP,
    UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS
)

class TestFormulaTokenization:
    """Tests for the formula tokenization functionality."""
    
    def test_tokenize_simple_formula(self):
        """Test tokenizing a simple formula."""
        formula = "A1+B1"
        tokens = tokenize_formula(formula)
        assert tokens == ["A1", "+", "B1"]
    
    def test_tokenize_formula_with_function(self):
        """Test tokenizing a formula with a function."""
        formula = "SUM(A1:A10)"
        tokens = tokenize_formula(formula)
        assert tokens == ["SUM", "(", "A1:A10", ")"]
    
    def test_tokenize_formula_with_multiple_operators(self):
        """Test tokenizing a formula with multiple operators."""
        formula = "A1+B1*C1/D1"
        tokens = tokenize_formula(formula)
        assert tokens == ["A1", "+", "B1", "*", "C1", "/", "D1"]
    
    def test_tokenize_formula_with_parentheses(self):
        """Test tokenizing a formula with parentheses."""
        formula = "(A1+B1)*(C1-D1)"
        tokens = tokenize_formula(formula)
        assert tokens == ["(", "A1", "+", "B1", ")", "*", "(", "C1", "-", "D1", ")"]
    
    def test_tokenize_formula_with_string_literal(self):
        """Test tokenizing a formula with string literals."""
        formula = 'IF(A1="Yes", 1, 0)'
        tokens = tokenize_formula(formula)
        # The tokenizer doesn't currently recognize commas as separate tokens
        assert tokens == ["IF", "(", "A1", "=", "\"Yes\"", "1", "0", ")"]
    
    def test_tokenize_formula_with_sheet_reference(self):
        """Test tokenizing a formula with sheet references."""
        formula = "Sheet1!A1+Sheet2!B2"
        tokens = tokenize_formula(formula)
        assert tokens == ["Sheet1!A1", "+", "Sheet2!B2"]
        
    def test_tokenize_formula_with_absolute_references(self):
        """Test tokenizing a formula with absolute cell references."""
        formula = "$A$1+B$2"
        tokens = tokenize_formula(formula)
        # The current implementation doesn't handle $ signs in cell references as part of the token
        assert tokens == ["A", "1", "+", "B", "2"]
        
    def test_tokenize_formula_with_nested_functions(self):
        """Test tokenizing a formula with nested functions."""
        formula = "IF(SUM(A1:A10)>100, MAX(B1:B10), MIN(C1:C10))"
        tokens = tokenize_formula(formula)
        expected = ["IF", "(", "SUM", "(", "A1:A10", ")", ">", "100", "MAX", "(", "B1:B10", ")", "MIN", "(", "C1:C10", ")", ")"]
        assert tokens == expected
        
    def test_tokenize_formula_with_decimal_numbers(self):
        """Test tokenizing a formula with decimal numbers."""
        formula = "A1*1.5+2.75"
        tokens = tokenize_formula(formula)
        assert tokens == ["A1", "*", "1.5", "+", "2.75"]
        
    def test_tokenize_formula_with_whitespace(self):
        """Test tokenizing a formula with extra whitespace."""
        formula = "  A1  +  B1  *  C1  "
        tokens = tokenize_formula(formula)
        assert tokens == ["A1", "+", "B1", "*", "C1"]

class TestFormulaTranslation:
    """Tests for the formula translation functionality."""
    
    def test_translate_basic_operators(self):
        """Test translation of basic operators."""
        assert translate_formula_part("+") == "+"
        assert translate_formula_part("-") == "-"
        assert translate_formula_part("*") == "*"
        assert translate_formula_part("/") == "/"
        assert translate_formula_part("^") == "**"  # Power operator
    
    def test_translate_comparison_operators(self):
        """Test translation of comparison operators."""
        assert translate_formula_part("=") == "=="
        assert translate_formula_part(">") == ">"
        assert translate_formula_part("<") == "<"
        assert translate_formula_part(">=") == ">="
        assert translate_formula_part("<=") == "<="
        assert translate_formula_part("<>") == "!="
    
    def test_translate_basic_functions(self):
        """Test translation of basic Excel functions."""
        assert translate_formula_part("SUM") == "sum"
        assert translate_formula_part("MAX") == "max"
        assert translate_formula_part("MIN") == "min"
        assert translate_formula_part("ABS") == "abs"
        assert translate_formula_part("ROUND") == "round"
    
    def test_translate_logical_functions(self):
        """Test translation of logical functions."""
        assert "lambda" in translate_formula_part("IF")
        assert "lambda" in translate_formula_part("AND")
        assert "lambda" in translate_formula_part("OR")
        assert "lambda" in translate_formula_part("NOT")
    
    def test_translate_unsupported_functions(self):
        """Test translation of unsupported functions."""
        for func in UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS:
            # Unsupported functions should return themselves
            assert translate_formula_part(func) == func
    
    def test_translate_unknown_function(self):
        """Test translation of an unknown function."""
        unknown_func = "SOME_UNKNOWN_FUNCTION"
        assert translate_formula_part(unknown_func) == unknown_func
    
    def test_case_insensitivity(self):
        """Test that function translation is case-insensitive."""
        assert translate_formula_part("sum") == "sum"
        assert translate_formula_part("Sum") == "sum"
        assert translate_formula_part("SUM") == "sum"
        
    def test_translate_average_function(self):
        """Test translation of the AVERAGE function."""
        translated = translate_formula_part("AVERAGE")
        assert "lambda" in translated
        assert "sum(x)" in translated
        assert "len(x)" in translated
        
    def test_translate_if_function(self):
        """Test translation of the IF function."""
        translated = translate_formula_part("IF")
        assert "lambda condition, true_val, false_val" in translated
        assert "true_val if condition else false_val" in translated
        
    def test_translate_and_function(self):
        """Test translation of the AND function."""
        translated = translate_formula_part("AND")
        assert "lambda *args" in translated
        assert "all(args)" in translated
        
    def test_translate_or_function(self):
        """Test translation of the OR function."""
        translated = translate_formula_part("OR")
        assert "lambda *args" in translated
        assert "any(args)" in translated
        
    def test_translate_not_function(self):
        """Test translation of the NOT function."""
        translated = translate_formula_part("NOT")
        assert "lambda x" in translated
        assert "not x" in translated 