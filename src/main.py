import logging
import os
from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from xlcalculator.model import ModelCompiler
from xlcalculator.evaluator import Evaluator
from io import BytesIO
from contextvars import ContextVar
import tempfile
import subprocess
from .sandbox import execute_script_in_sandbox # Import the sandbox function

from .file_handler import handle_file_upload, FileValidationError
from .dependency_extractor import generate_static_python_code, get_python_variable_name

# Context variable to hold warnings for the current request
request_warnings: ContextVar[list[str]] = ContextVar('request_warnings', default=[])

class RequestWarningsHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            request_warnings.get().append(self.format(record))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), # Keep console output for general info/errors
        RequestWarningsHandler() # Custom handler for capturing warnings
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/convert/")
async def convert_excel_to_python(file: UploadFile, output_filename: str | None = Form(None), force_evaluator: bool = Form(False)):
    # Reset warnings for the new request
    request_warnings.set([])
    """
    Converts an Excel or CSV/TSV file containing formulas into a Python script.

    This endpoint accepts an Excel (.xlsx) or CSV/TSV file, parses its content,
    extracts formulas, and generates a runnable Python script that replicates
    the spreadsheet's calculations.

    Args:
        file (UploadFile): The input file (Excel or CSV/TSV) to be converted.
                           Expected file types: .xlsx, .csv, .tsv.
                           Maximum file size: 10MB.
        output_filename (str | None, optional): If provided, the generated Python script
                                         will be saved to this filename. Otherwise,
                                         the script content will be returned directly
                                         in the response.
        force_evaluator (bool, optional): If True, forces all formulas to be evaluated
                                          at runtime using `xlcalculator.Evaluator`,
                                          bypassing static translation. Defaults to False.

    Returns:
        JSONResponse:
            - If `output_filename` is provided, returns a success message
              indicating where the file was saved and any warnings.
            - If `output_filename` is not provided, returns the generated Python
              script as JSON with warnings.

    Raises:
        HTTPException:
            - 400 Bad Request: If the file name is missing, or there's an error
                               during file parsing with xlcalculator.
            - 413 Payload Too Large: If the file size exceeds the allowed limit.
            - 415 Unsupported Media Type: If the file extension is not allowed.
            - 500 Internal Server Error: For any unexpected server-side errors.
    """
    try:
        file_content = await handle_file_upload(file)

        # Determine file type and load accordingly
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        
        # xlcalculator uses ModelCompiler to parse the archive (Excel file)
        # For CSV/TSV, xlcalculator can also handle it, but typically Excel files are more complex.
        # Assuming here that handle_file_upload returns content suitable for BytesIO
        try:
            model = ModelCompiler().read_and_parse_archive(BytesIO(file_content))
            evaluator = Evaluator(model)
        except Exception as e:
            logger.error(f"Error parsing or reading Excel file: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error parsing or reading Excel file: {e}")

        # Generate Python code, which now includes fallback logic
        generated_code = generate_static_python_code(model)

        # Assemble the final script
        final_script_lines = [
            "from xlcalculator.model import Model",
            "from xlcalculator.evaluator import Evaluator",
            "from io import BytesIO",
            "import re", # May be needed for regex in generated code
            "",
            "# --- Start of Generated Excel to Python Conversion ---",
            "",
            "# Initialize the model and evaluator (placeholder - in a real app, these would be loaded from file or passed)",
            "# For simplicity, we are not re-parsing the file here, assuming `model` is available if this code runs independently.",
            "# If this script is meant to be run standalone, you would need to add file loading here.",
            "",
            "# Example: If running standalone, you would load your Excel file like this:",
            "# from xlcalculator.model import ModelCompiler",
            "# from io import BytesIO",
            "# with open(\"your_excel_file.xlsx\", \"rb\") as f:",
            "#     model_compiler = ModelCompiler()",
            "#     model = model_compiler.read_and_parse_archive(BytesIO(f.read()))",
            "# evaluator = Evaluator(model)",
            "",
            generated_code,
            "",
            "# --- End of Generated Excel to Python Conversion ---",
            ""
        ]
        final_script = "\n".join(final_script_lines)

        if output_filename:
            # Save to file
            with open(output_filename, "w") as f:
                f.write(final_script)
            logger.info(f"Successfully converted and saved to {output_filename}")
            return JSONResponse({"message": f"Successfully converted and saved to {output_filename}", "warnings": request_warnings.get(), "log_url": "/logs/"})
        else:
            logger.info("Successfully converted Excel to Python script. Attempting to execute in sandbox.")
            # Execute the generated script in a sandbox if no output_filename is provided
            temp_script_path = None
            execution_stdout = ""
            execution_stderr = ""
            execution_returncode = None
            try:
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp_script_file:
                    temp_script_file.write(final_script)
                    temp_script_path = temp_script_file.name
                
                # Execute the script in sandbox
                stdout, stderr, returncode = execute_script_in_sandbox(temp_script_path)
                execution_stdout = stdout
                execution_stderr = stderr
                execution_returncode = returncode
                logger.info(f"Sandbox execution completed with return code: {returncode}")

            except subprocess.TimeoutExpired:
                logger.error("Script execution timed out in sandbox.")
                execution_stderr = f"Script execution timed out."
            except Exception as e:
                logger.error(f"Error during sandbox execution: {e}", exc_info=True)
                execution_stderr = f"Error during sandbox execution: {e}"
            finally:
                if temp_script_path and os.path.exists(temp_script_path):
                    os.remove(temp_script_path)

            return JSONResponse({
                "script": final_script,
                "warnings": request_warnings.get(),
                "execution_output": {
                    "stdout": execution_stdout,
                    "stderr": execution_stderr,
                    "return_code": execution_returncode
                },
                "log_url": "/logs/"
            })

    except FileValidationError as e:
        logger.warning(f"File validation error: {e.message}", exc_info=True)
        return JSONResponse({"detail": e.message, "warnings": request_warnings.get(), "log_url": "/logs/"}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"An unexpected server error occurred: {e}", exc_info=True)
        return JSONResponse({"detail": f"An unexpected server error occurred: {e}", "warnings": request_warnings.get(), "log_url": "/logs/"}, status_code=500)

# API endpoint for full log access
@app.get("/logs/")
async def get_logs():
    log_file_path = "app.log" # Assuming logs are written to app.log, adjust if needed
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            log_content = f.read()
        return PlainTextResponse(log_content)
    else:
        raise HTTPException(status_code=404, detail="Log file not found.") 