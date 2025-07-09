import os
import pytest
from fastapi import UploadFile
from io import BytesIO
from unittest.mock import MagicMock, AsyncMock, patch

from src.file_handler import (
    handle_file_upload,
    FileValidationError,
    InvalidFileSizeError,
    InvalidFileExtensionError
)

class TestFileValidation:
    """Tests for file validation functionality."""

    @pytest.mark.asyncio
    async def test_valid_xlsx_file(self):
        """Test that a valid XLSX file passes validation."""
        # Create a mock file with valid extension and size
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.xlsx"
        mock_file.read = AsyncMock(return_value=b"x" * 1024)  # 1KB file
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert file_content == b"x" * 1024

    @pytest.mark.asyncio
    async def test_valid_csv_file(self):
        """Test that a valid CSV file passes validation."""
        # Create a mock file with valid extension and size
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.read = AsyncMock(return_value=b"x" * 1024)  # 1KB file
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert file_content == b"x" * 1024

    @pytest.mark.asyncio
    async def test_valid_tsv_file(self):
        """Test that a valid TSV file passes validation."""
        # Create a mock file with valid extension and size
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.tsv"
        mock_file.read = AsyncMock(return_value=b"x" * 1024)  # 1KB file
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert file_content == b"x" * 1024

    @pytest.mark.asyncio
    async def test_file_too_large(self):
        """Test that a file that's too large is rejected."""
        # Create a mock file that's too large
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.xlsx"
        mock_file.read = AsyncMock(return_value=b"x" * (11 * 1024 * 1024))
        
        # Call the function and expect an exception
        with pytest.raises(FileValidationError) as excinfo:
            await handle_file_upload(mock_file)
        
        # Verify the exception message
        assert "File size exceeds 10MB limit" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_invalid_extension(self):
        """Test that a file with an invalid extension is rejected."""
        # Create a mock file with invalid extension
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"x" * 1024)
        
        # Call the function and expect an exception
        with pytest.raises(FileValidationError) as excinfo:
            await handle_file_upload(mock_file)
        
        # Verify the exception message
        assert "Invalid file extension: .pdf" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_missing_filename(self):
        """Test that a file with no filename is rejected."""
        # Create a mock file with no filename
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = None
        mock_file.read = AsyncMock(return_value=b"x" * 1024)
        
        # Call the function and expect an exception
        with pytest.raises(FileValidationError) as excinfo:
            await handle_file_upload(mock_file)
        
        # Verify the exception message
        assert "File name is missing" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_read_error(self):
        """Test that an error during file reading is handled properly."""
        # Create a mock file that raises an error when read
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.xlsx"
        mock_file.read = AsyncMock(side_effect=Exception("Read error"))
        
        # Call the function and expect an exception
        with pytest.raises(FileValidationError) as excinfo:
            await handle_file_upload(mock_file)
        
        # Verify the exception message
        assert "Could not read file content" in str(excinfo.value)
        
    @pytest.mark.asyncio
    async def test_empty_file(self):
        """Test handling of an empty file."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "empty.xlsx"
        mock_file.read = AsyncMock(return_value=b"")  # Empty file
        
        # Empty files should be valid as long as they have the right extension
        file_content = await handle_file_upload(mock_file)
        assert file_content == b""
        
    @pytest.mark.asyncio
    async def test_uppercase_extension(self):
        """Test that file extensions are case-insensitive."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.XLSX"  # Uppercase extension
        mock_file.read = AsyncMock(return_value=b"x" * 1024)
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert file_content == b"x" * 1024
        
    @pytest.mark.asyncio
    async def test_filename_with_dots(self):
        """Test handling of filenames with multiple dots."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.backup.xlsx"  # Multiple dots in filename
        mock_file.read = AsyncMock(return_value=b"x" * 1024)
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert file_content == b"x" * 1024
        
    @pytest.mark.asyncio
    async def test_exactly_max_size(self):
        """Test a file that's exactly at the maximum allowed size."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.xlsx"
        # Exactly 10MB file (the limit)
        mock_file.read = AsyncMock(return_value=b"x" * (10 * 1024 * 1024))
        
        # Call the function and assert no exceptions are raised
        file_content = await handle_file_upload(mock_file)
        assert len(file_content) == 10 * 1024 * 1024 