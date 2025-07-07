import argparse
import os
import shutil
import sys
from utils.file_validation import validate_uploaded_file, InvalidFileTypeError, FileTooLargeError

TEMP_DIR = "./temp_uploads"

def setup_temp_dir():
    """Ensures the temporary upload directory exists."""
    os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_temp_dir():
    """Removes the temporary upload directory."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

def cli_main():
    parser = argparse.ArgumentParser(description="Excel to Python Formula Converter CLI")
    parser.add_argument("file_path", type=str, help="Path to the .xlsx, .csv, or .tsv file")
    parser.add_argument("--run", action="store_true", help="Execute the generated Python script")

    args = parser.parse_args()

    setup_temp_dir()
    try:
        # Construct the full path to the source file
        source_file_path = args.file_path
        if not os.path.isabs(source_file_path):
            # If relative, make it absolute for consistent copying
            source_file_path = os.path.abspath(source_file_path)

        # Simulate temporary storage by copying the file
        temp_file_path = os.path.join(TEMP_DIR, os.path.basename(source_file_path))

        # Check if source file exists before attempting to copy
        if not os.path.exists(source_file_path):
            sys.stderr.write(f"Error: File not found at '{args.file_path}'\n")
            return

        shutil.copy(source_file_path, temp_file_path)

        validate_uploaded_file(source_file_path, temp_file_path)
        sys.stdout.write(f"File '{args.file_path}' validated successfully and stored temporarily.\n")
        # Further processing would go here in later tasks

    except InvalidFileTypeError as e:
        sys.stderr.write(f"Error: {e.message}\n")
    except FileTooLargeError as e:
        sys.stderr.write(f"Error: {e.message}\n")
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
    finally:
        cleanup_temp_dir()

if __name__ == "__main__":
    cli_main() 