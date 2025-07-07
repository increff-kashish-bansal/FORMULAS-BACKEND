import os
import pandas as pd
from typing import Dict
from utils.logger import AppLogger # Import the custom logger

# Instantiate the custom logger
app_logger = AppLogger(__name__)

def get_excel_column_letter(col_idx: int) -> str:
    """Converts a 0-indexed column integer to an Excel column letter (e.g., 0 -> A, 26 -> AA)."""
    letter = ""
    while col_idx >= 0:
        letter = chr(65 + (col_idx % 26)) + letter
        col_idx = (col_idx // 26) - 1
    return letter

def parse_csv_tsv_file(file_path: str) -> list[Dict[str, str]]:
    """
    Parses a CSV or TSV file to identify potential formulas.
    Args:
        file_path (str): The path to the CSV/TSV file.
    Returns:
        list[Dict[str, str]]: A list of dictionaries containing potential raw formula information.
    """
    extracted_formulas_raw = []
    filename = os.path.basename(file_path)
    file_extension = os.path.splitext(filename)[1].lower()
    delimiter = ',' if file_extension == '.csv' else '\t'

    try:
        # Read the file into a pandas DataFrame
        df = pd.read_csv(file_path, delimiter=delimiter, header=None)
        app_logger.info(
            f"Processing file: {filename}",
            context={'file': filename, 'extension': file_extension}
        )

        # For CSV/TSV, we treat the entire file as a single 'sheet'
        sheet_name = filename # Or a default like 'Sheet1'

        # Iterate through cells to find strings that look like formulas (start with '=')
        for row_idx in df.index:
            row = df.loc[row_idx]
            for col_idx, cell_value in enumerate(row):
                if isinstance(cell_value, str) and cell_value.strip().startswith('='):
                    # Convert column index to Excel-style column letter
                    col_letter = get_excel_column_letter(col_idx)

                    # row_idx obtained from df.index is already a pure integer
                    cell_address = f"{col_letter}{row_idx + 1}"
                    formula_str = cell_value.strip()
                    app_logger.info(
                        f"Found potential formula in {sheet_name}!{cell_address}: {formula_str}",
                        context={'sheet': sheet_name, 'cell': cell_address, 'formula': formula_str}
                    )
                    extracted_formulas_raw.append({
                        "file_path": file_path,
                        "sheet_name": sheet_name,
                        "cell_address": cell_address,
                        "formula_string": formula_str
                    })
    except Exception as e:
        app_logger.error(f"Error parsing CSV/TSV file {file_path}: {e}", context={'file': file_path, 'error': str(e)})

    return extracted_formulas_raw 