import argparse
import sys
import tempfile # Import tempfile for temporary file handling
import os # Import os for file path manipulation
import subprocess
import logging

from .main import convert_excel_to_python # Import the FastAPI endpoint function
from .sandbox import execute_script_in_sandbox, MAX_CPU_TIME # Import the sandbox execution function and MAX_CPU_TIME
from fastapi import UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from io import BytesIO

# Configure logging for CLI. Warnings and errors go to stderr.
# This basicConfig will apply to all loggers unless overridden.
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Default to stdout
    ]
)

# Create a separate handler for WARNING and ERROR to direct to stderr
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# Add the error handler to the root logger
logging.getLogger().addHandler(error_handler)

# Set the root logger level, for example, to INFO to catch INFO, WARNING, ERROR
logging.getLogger().setLevel(logging.INFO)

# Get a specific logger for this module (optional, but good practice)
logger = logging.getLogger(__name__)

class CLIUploadFile(UploadFile):
    """
    A mock UploadFile class to adapt file-like objects for FastAPI endpoint.
    """
    def __init__(self, filename: str, file_content: bytes):
        super().__init__(filename=filename, file=BytesIO(file_content))

async def main():
    parser = argparse.ArgumentParser(description="Convert Excel/CSV/TSV files with formulas to static Python code.")
    parser.add_argument("input_file", type=str, help="Path to the input Excel/CSV/TSV file.")
    parser.add_argument("--output", "-o", type=str, help="Optional: Path to save the generated Python script. If not provided, output will be printed to stdout.")
    parser.add_argument("--force-evaluator", action="store_true", help="If set, forces all formulas to be evaluated at runtime using xlcalculator.Evaluator, bypassing static translation.")
    
    args = parser.parse_args()
    
    try:
        with open(args.input_file, "rb") as f:
            file_content = f.read()
        
        # Create a mock UploadFile object for the FastAPI endpoint
        mock_upload_file = CLIUploadFile(filename=args.input_file, file_content=file_content)

        # Call the FastAPI endpoint logic directly
        # The convert_excel_to_python function expects a FastAPI UploadFile object and output_filename
        logger.info(f"Processing file: {args.input_file}")
        response = await convert_excel_to_python(
            file=mock_upload_file, 
            output_filename=None,
            force_evaluator=args.force_evaluator
        ) # Don't save directly here
        
        if isinstance(response, PlainTextResponse):
            generated_script_content = bytes(response.body).decode()
            
            # Create a temporary file to save the generated script for sandbox execution
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp_script_file:
                temp_script_file.write(generated_script_content)
                temp_script_path = temp_script_file.name
            
            try:
                logger.info("Executing generated script in sandbox...")
                stdout, stderr, returncode = execute_script_in_sandbox(temp_script_path)
                if stdout:
                    logger.info(f"Sandbox Output (STDOUT):\n{stdout}")
                if stderr:
                    logger.error(f"Sandbox Errors (STDERR):\n{stderr}") # Direct stderr to logger.error
                logger.info(f"Sandbox Exit Code: {returncode}")

            except subprocess.TimeoutExpired:
                logger.error(f"Script execution timed out after {MAX_CPU_TIME} seconds.")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                logger.error(f"Script execution failed with exit code {e.returncode}.\nOutput: {e.output}\nError: {e.stderr}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"An error occurred during sandbox execution: {e}", exc_info=True)
                sys.exit(1)
            finally:
                # Clean up the temporary script file
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)

            # If output_filename is provided, save the generated script to it
            if args.output:
                with open(args.output, "w") as f:
                    f.write(generated_script_content)
                logger.info(f"Generated Python script saved to {args.output}")
            else:
                logger.info("Generated Python script content printed to console.")

        else:
            # Handle other response types if necessary, though PlainTextResponse is expected
            logger.warning("Unexpected response type from conversion function.")

    except FileNotFoundError:
        logger.error(f"Error: Input file not found at {args.input_file}")
        sys.exit(1)
    except HTTPException as e:
        logger.error(f"Error processing file: {e.detail}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

def main_wrapper():
    """Entry point for the console script."""
    import asyncio
    asyncio.run(main())
    
if __name__ == "__main__":
    # argparse does not support async directly in __main__ context easily,
    # so we run it using asyncio.run() if needed for local testing.
    # For direct CLI execution, a synchronous approach might be more common,
    # or FastAPI's internal mechanisms handle the async calls.
    main_wrapper() 