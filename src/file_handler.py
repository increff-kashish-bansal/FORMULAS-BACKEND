import os
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InvalidFileSizeError(FileValidationError):
    """Custom exception for invalid file size."""
    def __init__(self, message: str = "File size exceeds limit."):
        super().__init__(message, status_code=413)

class InvalidFileExtensionError(FileValidationError):
    """Custom exception for invalid file extension."""
    def __init__(self, message: str = "Invalid file extension."):
        super().__init__(message, status_code=415)

async def handle_file_upload(file: UploadFile):
    """
    Handles the uploaded file, including temporary storage or in-memory representation.
    """
    # In a real application, you would save the file to disk or process it in memory.
    # For now, we'll just read its content for validation purposes.
    try:
        file_content = await file.read()
        # Validate file size
        MAX_FILE_SIZE_MB = 10
        if len(file_content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise InvalidFileSizeError(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")
        # Validate file extension
        ALLOWED_EXTENSIONS = ['xlsx', 'csv', 'tsv']
        if file.filename is None:
            raise FileValidationError("File name is missing.", status_code=400)
        file_extension = os.path.splitext(file.filename)[1].lstrip('.').lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: .{file_extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
            raise InvalidFileExtensionError(f"Invalid file extension: .{file_extension}. Allowed extensions are {', '.join(ALLOWED_EXTENSIONS)}.")
        logger.info(f"File {file.filename} (size: {len(file_content)} bytes) validated successfully.")
        return file_content
    except Exception as e:
        logger.error(f"Error handling file upload for {file.filename}: {e}", exc_info=True)
        raise FileValidationError(f"Could not read file content: {e}", status_code=500) 