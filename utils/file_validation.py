import os

# Custom Exceptions for file validation
class InvalidFileTypeError(Exception):
    """Raised when the file type is not supported."""
    def __init__(self, message="Unsupported file type. Only .xlsx, .csv, and .tsv are allowed."):
        self.message = message
        super().__init__(self.message)

class FileTooLargeError(Exception):
    """Raised when the file size exceeds the allowed limit."""
    def __init__(self, message="File size exceeds the 10MB limit."):
        self.message = message
        super().__init__(self.message)

def validate_file_type(filename: str):
    """
    Validates if the file has a supported extension (.xlsx, .csv, .tsv).
    Args:
        filename (str): The name of the file to validate.
    Raises:
        InvalidFileTypeError: If the file extension is not supported.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.xlsx', '.csv', '.tsv']:
        raise InvalidFileTypeError()

def validate_file_size(file_path: str, max_size_mb: int = 10):
    """
    Validates if the file size is within the allowed limit.
    Args:
        file_path (str): The path to the file.
        max_size_mb (int): The maximum allowed file size in MB.
    Raises:
        FileTooLargeError: If the file size exceeds the limit.
    """
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise FileTooLargeError()

def validate_uploaded_file(filename: str, file_path: str, max_size_mb: int = 10):
    """
    Performs a comprehensive validation for uploaded files, checking both type and size.
    Args:
        filename (str): The original name of the uploaded file.
        file_path (str): The temporary path where the file is stored.
        max_size_mb (int): The maximum allowed file size in MB.
    Raises:
        InvalidFileTypeError: If the file extension is not supported.
        FileTooLargeError: If the file size exceeds the limit.
    """
    validate_file_type(filename)
    validate_file_size(file_path, max_size_mb) 