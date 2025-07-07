import formulas
from utils.logger import AppLogger

app_logger = AppLogger(__name__)

def register_custom_excel_functions():
    """
    Registers custom Excel functions with the formulas library.
    """
    FUNCTIONS = formulas.get_functions()

    # Example: Custom implementation for XLOOKUP (simplified)
    # In a real scenario, this would be a more robust implementation.
    # The formulas library expects functions to handle Array objects.
    def xlookup_custom(lookup_value, lookup_array, return_array, if_not_found=None, match_mode=0, search_mode=1):
        app_logger.info("Executing custom XLOOKUP function.", context={'lookup_value': lookup_value, 'match_mode': match_mode})
        # Simplified logic for demonstration
        try:
            lookup_list = lookup_array.flatten().tolist()
            return_list = return_array.flatten().tolist()
            for i, val in enumerate(lookup_list):
                if val == lookup_value:
                    return formulas.Array(return_list[i])
            if if_not_found is not None:
                return formulas.Array(if_not_found)
            return formulas.ExcelError.VALUE
        except Exception as e:
            app_logger.error(f"Error in custom XLOOKUP: {e}", context={'error': str(e)})
            return formulas.ExcelError.VALUE

    FUNCTIONS['XLOOKUP'] = xlookup_custom

    # Add more custom functions here as needed
    # FUNCTIONS['MY_CUSTOM_SUM'] = lambda *args: sum(formulas.flatten(args))

    app_logger.info("Custom Excel functions registered.") 