import re
import logging

logger = logging.getLogger(__name__)

EXCEL_FUNCTION_MAP = {
    # Arithmetic operations
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "^": "**", # Excel's power operator

    # Basic functions
    "SUM": "sum",
    "AVERAGE": "lambda x: sum(x) / len(x)", # Simplified for now, needs proper handling of ranges
    "IF": "lambda condition, true_val, false_val: true_val if condition else false_val",
    "AND": "lambda *args: all(args)",
    "OR": "lambda *args: any(args)",
    "NOT": "lambda x: not x",
    "ABS": "abs",
    "ROUND": "round",
    "MAX": "max",
    "MIN": "min",

    # Logical operators
    "=": "==",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "<>": "!=",
}

UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS = {
    "INDIRECT",
    "OFFSET",
    "RAND",
    "NOW",
    "TODAY",
    "CELL",
    "N",
    "T",
    "INFO",
    # Add other functions here that are known to be difficult for static translation
}

def translate_formula_part(excel_part: str) -> str:
    """
    Translates a single Excel formula part (operator or function name) to its Python equivalent.
    """
    translated = EXCEL_FUNCTION_MAP.get(excel_part.upper())
    if translated is None:
        if excel_part.upper() in UNSUPPORTED_OR_VOLATILE_EXCEL_FUNCTIONS:
            logger.warning(f"Unsupported or volatile Excel function encountered: {excel_part}. This will require runtime evaluation.")
        else:
            logger.warning(f"Unknown Excel formula part encountered: {excel_part}. Returning as is.")
        return excel_part
    return translated

def tokenize_formula(formula: str) -> list[str]:
    """
    Tokenizes an Excel formula string into a list of meaningful parts.
    This is a basic tokenizer and may need to be expanded for full Excel formula complexity.
    """
    tokens = []
    # Regular expression to match various Excel formula components:
    # - Cell references (e.g., A1, $B$2, Sheet1!C3)
    # - Operators (+, -, *, /, =, <>, >, <, >=, <=, & (for concatenation))
    # - Function names (e.g., SUM, IF, VLOOKUP)
    # - Numbers (integers, decimals)
    # - Strings (enclosed in double quotes)
    # - Parentheses ()

    # Regex components:
    # Cell references: (?:[A-Za-z_][A-Za-z0-9_]*!)?[A-Za-z]+\d+(?::[A-Za-z]+\d+)?(?:\$[A-Za-z]+\$\d+)?
    # This matches optional sheet name, column letter(s), row number, optional range, optional absolute references.
    # More robust cell reference regex might be needed for edge cases.

    # String literals: "(?:\\"|[^"])*" (matches "..." with escaped quotes)
    # Numbers: \d+(?:\.\d+)?
    # Operators: \s*([-+*/=<>!&^])\s*
    # Function names and named ranges: [A-Za-z_][A-Za-z0-9_]*

    # Combining them into a single pattern
    token_pattern = re.compile(r"""
        ("(?:\\"|[^"])*")       |   # 1: String literals
        ((?:[A-Za-z_][A-Za-z0-9_]*!)?[A-Za-z]+\d+(?::[A-Za-z]+\d+)?(?:\$[A-Za-z]+\$\d+)?) |   # 2: Cell references (A1, $B$2, Sheet1!C3, A1:B2)
        ([+\-*/=<>!&^])          |   # 3: Operators
        ([A-Za-z_][A-Za-z0-9_]*)  |   # 4: Function names or named ranges
        (\d+(?:\.\d+)?)         |   # 5: Numbers
        ([()])                    |   # 6: Parentheses
        \s+                          # Ignore whitespace
    """, re.VERBOSE)

    for match in token_pattern.finditer(formula):
        # Extract the matched group that is not None
        for i in range(1, 7): # Iterate through all capturing groups
            if match.group(i) is not None:
                tokens.append(match.group(i))
                break
        else:
            # This case should ideally not be reached if the regex covers all possibilities
            # but good for debugging unrecognized parts
            unmatched_text = formula[match.end()-len(match.group()):match.end()]
            logger.warning(f"Unrecognized part in formula during tokenization: '{unmatched_text}'")

    return tokens 