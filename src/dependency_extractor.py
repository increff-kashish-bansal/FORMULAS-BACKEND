from xlcalculator.model import Model
from collections import defaultdict
from .formula_translator import translate_formula_part, tokenize_formula, UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS
import re
import logging

logger = logging.getLogger(__name__)

def extract_formula_dependencies(model: Model) -> dict:
    """
    Extracts formula dependency relationships from the xlcalculator model.

    Args:
        model: The xlcalculator Model object.

    Returns:
        A dictionary where keys are cell addresses (e.g., 'Sheet1!A1') and values
        are lists of their direct precedents (dependencies).
    """
    dependencies = {}
    for cell_address, cell in model.cells.items():
        if cell.formula:
            # xlcalculator's Cell object provides direct access to precedents
            precedents = [p.formula_address for p in cell.precedents]
            dependencies[cell.formula_address] = precedents
    return dependencies

def get_evaluation_order(model: Model) -> list:
    """
    Performs a topological sort on the cells to determine their evaluation order.

    Args:
        model: The xlcalculator Model object.

    Returns:
        A list of cell addresses in topological order.
    """
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_cells = set()

    for cell_address, cell in model.cells.items():
        all_cells.add(cell_address)
        if in_degree[cell_address] == 0:
            in_degree[cell_address] = 0 # Ensure all cells are initialized in in_degree
        if cell.formula:
            for precedent_cell in cell.precedents:
                graph[precedent_cell.formula_address].append(cell_address)
                in_degree[cell_address] += 1

    # Add cells with no dependencies to the queue
    queue = []
    for cell_address in all_cells:
        if in_degree[cell_address] == 0:
            queue.append(cell_address)

    evaluation_order = []
    while queue:
        current_cell = queue.pop(0)
        evaluation_order.append(current_cell)

        for neighbor in graph[current_cell]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for circular dependencies (if evaluation_order doesn't contain all cells)
    if len(evaluation_order) != len(all_cells):
        # This indicates a circular dependency or an issue in graph construction
        # For simplicity, we'll just return the current order, but in a real app,
        # you might want to raise an error or log a warning.
        pass # Handle circular dependency if necessary

    return evaluation_order

def extract_headers(model: Model) -> dict[str, dict[str, str]]:
    """
    Extracts headers from the first row of each sheet in the xlcalculator model.
    Returns a dictionary mapping sheet names to another dictionary of column letter to header text.
    """
    headers_by_sheet = defaultdict(dict)
    # xlcalculator.Model does not have a 'sheets' attribute directly accessible in this manner.
    # We need to iterate through all cells and infer sheets from cell addresses.
    for cell_address, cell in model.cells.items():
        match = re.match(r'(.+?)!([A-Za-z]+)(\d+)', cell_address)
        if match:
            sheet_name, col_letter, row_number_str = match.groups()
            row_number = int(row_number_str)
            if row_number == 1 and cell.value:
                headers_by_sheet[sheet_name][col_letter] = str(cell.value)
    return headers_by_sheet

def get_python_variable_name(cell_address: str, headers_by_sheet: dict[str, dict[str, str]]) -> str:
    """
    Generates a Python-compatible variable name for a given Excel cell address.
    Prioritizes Header > Cell Reference (e.g., 'Sheet1!A1' to 'sheet1_A1').
    """
    sheet_name_match = re.match(r'(.+?)!(.*)', cell_address)
    if sheet_name_match:
        sheet_name = sheet_name_match.group(1)
        base_cell_address = sheet_name_match.group(2)
    else:
        sheet_name = None
        base_cell_address = cell_address

    col_match = re.match(r'([A-Za-z]+)(\d+)', base_cell_address)
    if col_match:
        col_letter = col_match.group(1)
        # Attempt to use header if available
        if sheet_name and sheet_name in headers_by_sheet and col_letter in headers_by_sheet[sheet_name]:
            header_name = headers_by_sheet[sheet_name][col_letter]
            # Clean header name for Python variable: replace spaces/special chars, add sheet prefix
            cleaned_header_name = re.sub(r'[^a-zA-Z0-9_]', '_', header_name)
            logger.info(f"Inferred variable name for {cell_address} from header '{header_name}': {sheet_name.lower()}_{cleaned_header_name}")
            return f"{sheet_name.lower()}_{cleaned_header_name}"

    # Fallback to cleaned cell reference if no header matches or no sheet name
    variable_name = re.sub(r'[^a-zA-Z0-9_]', '_', cell_address)
    if not re.match(r'^[a-zA-Z_]', variable_name):
        variable_name = '_' + variable_name
    logger.warning(f"Falling back to cell reference for variable name for {cell_address}: {variable_name.lower()}")
    return variable_name.lower()

def generate_static_python_code(model: Model, force_evaluator: bool = False) -> str:
    """
    Generates static Python code for the formulas in the xlcalculator model.
    This function aims to translate simple formulas into direct Python expressions.

    Args:
        model: The xlcalculator Model object.
        force_evaluator (bool): If True, forces all formulas to be evaluated at runtime
                                using `xlcalculator.Evaluator`, bypassing static translation.

    Returns:
        A string containing the generated Python code.
    """
    python_code_lines = []
    evaluation_order = get_evaluation_order(model)

    headers_by_sheet = extract_headers(model) # Extract headers once

    # Initialize cell values (assuming all inputs are initially 0 or empty for static code)
    # In a real scenario, these would come from user input or source data.
    for cell_address in evaluation_order:
        cell_var_name = get_python_variable_name(cell_address, headers_by_sheet) # Pass headers
        python_code_lines.append(f"{cell_var_name} = 0 # Initialize for {cell_address}") # Placeholder initialization

    python_code_lines.append("\n# Translated Formulas\n")

    for cell_address in evaluation_order:
        cell = model.cells.get(cell_address)
        if cell and cell.formula:
            # Check for unsupported or volatile functions, or if force_evaluator is True
            formula_text = cell.formula
            requires_runtime_fallback = force_evaluator # If force_evaluator is true, always use runtime
            if not requires_runtime_fallback:
                for func_name in UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS:
                    if re.search(r' ' + re.escape(func_name) + r' ', formula_text, re.IGNORECASE):
                        requires_runtime_fallback = True
                        break

            cell_var_name = get_python_variable_name(cell_address, headers_by_sheet) # Pass headers

            if requires_runtime_fallback:
                if force_evaluator:
                    logger.info(f"Formula for cell {cell_address} will be evaluated at runtime due to force_evaluator flag.")
                else:
                    logger.warning(f"Formula for cell {cell_address} contains unsupported/volatile functions. Falling back to runtime evaluation.")
                python_code_lines.append(f"# NOTE: Cell {cell_address} will be evaluated at runtime using xlcalculator.Evaluator.")
                python_code_lines.append(f"{cell_var_name} = evaluator.evaluate(model, '{cell_address}') # Runtime evaluation")
            else:
                # Tokenize the formula
                tokens = tokenize_formula(formula_text)
                translated_parts = []
                for token in tokens:
                    if re.match(r'^[A-Za-z]+[0-9]+(?::[A-Za-z]+[0-9]+)?$', token) or re.match(r'^[A-Za-z_][A-Za-z0-9_]*![A-Za-z]+[0-9]+(?::[A-Za-z]+[0-9]+)?$', token):
                        # It's a cell reference, convert to Python variable name
                        translated_parts.append(get_python_variable_name(token, headers_by_sheet)) # Pass headers
                    else:
                        # Translate other parts (operators, functions, literals)
                        translated_parts.append(translate_formula_part(token))
                
                translated_formula = "".join(translated_parts)
                python_code_lines.append(f"{cell_var_name} = {translated_formula}")
    return "\n".join(python_code_lines) 