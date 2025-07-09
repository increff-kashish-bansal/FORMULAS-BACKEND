import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import tempfile
import asyncio
from io import BytesIO, StringIO
import subprocess

from src.cli import CLIUploadFile

class TestCLI:
    """Tests for the command-line interface."""

    @pytest.fixture
    def mock_file_content(self):
        """Create a mock file content."""
        return b"mock excel file content"

    @pytest.fixture
    def temp_excel_file(self, tmp_path):
        """Create a temporary Excel file."""
        temp_file_path = tmp_path / "test.xlsx"
        with open(temp_file_path, "wb") as f:
            f.write(b"mock excel file content")
        yield str(temp_file_path)
        # Clean up
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    @pytest.fixture
    def temp_output_file(self, tmp_path):
        """Create a temporary output file path."""
        temp_file_path = tmp_path / "output.py"
        yield str(temp_file_path)
        # Clean up
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    @pytest.fixture
    def mock_stdout(self):
        """Capture stdout for testing."""
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        yield mystdout
        sys.stdout = old_stdout

    @pytest.fixture
    def mock_stderr(self):
        """Capture stderr for testing."""
        old_stderr = sys.stderr
        sys.stderr = mystderr = StringIO()
        yield mystderr
        sys.stderr = old_stderr

    def test_cli_upload_file(self, mock_file_content):
        """Test the CLIUploadFile class."""
        # Create a CLIUploadFile instance
        file_path = "test.xlsx"
        cli_file = CLIUploadFile(filename=file_path, file_content=mock_file_content)
        
        # Test properties
        assert cli_file.filename == file_path
        
        # Test read method - CLIUploadFile inherits from UploadFile which has async read
        async def test_read():
            content = await cli_file.read()
            assert content == mock_file_content
        
        # Run the async test function
        asyncio.run(test_read())

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_function(self, mock_cli_upload, mock_convert, mock_argparse, mock_stdout, mock_stderr):
        """Test the main function of the CLI."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.xlsx"
        mock_args.output = None
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.body = b"# Generated Python code"
        mock_convert.return_value = mock_response
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch execute_script_in_sandbox to avoid actual execution
        with patch("builtins.open", mock_open):
            with patch("src.cli.execute_script_in_sandbox", return_value=("Output", "", 0)):
                # Patch os.path.exists and os.remove for temp file cleanup
                with patch("os.path.exists", return_value=True), patch("os.remove"):
                    # Import main here to avoid early argparse initialization
                    from src.cli import main
                    await main()
        
        # Verify that convert_excel_to_python was called
        mock_convert.assert_called_once()
        assert "Generated Python script content" in mock_stdout.getvalue()

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_with_output_file(self, mock_cli_upload, mock_convert, mock_argparse, temp_output_file, mock_stdout):
        """Test the main function with an output file specified."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.xlsx"
        mock_args.output = temp_output_file
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.body = b"# Generated Python code"
        mock_convert.return_value = mock_response
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch execute_script_in_sandbox to avoid actual execution
        with patch("builtins.open", mock_open):
            with patch("src.cli.execute_script_in_sandbox", return_value=("Output", "", 0)):
                # Patch os.path.exists and os.remove for temp file cleanup
                with patch("os.path.exists", return_value=True), patch("os.remove"):
                    # Import main here to avoid early argparse initialization
                    from src.cli import main
                    await main()
        
        # Verify that convert_excel_to_python was called
        mock_convert.assert_called_once()
        assert f"Generated Python script saved to {temp_output_file}" in mock_stdout.getvalue()

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_with_force_evaluator(self, mock_cli_upload, mock_convert, mock_argparse):
        """Test the main function with force_evaluator flag."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.xlsx"
        mock_args.output = None
        mock_args.force_evaluator = True
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.body = b"# Generated Python code"
        mock_convert.return_value = mock_response
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch execute_script_in_sandbox to avoid actual execution
        with patch("builtins.open", mock_open):
            with patch("src.cli.execute_script_in_sandbox", return_value=("Output", "", 0)):
                # Patch os.path.exists and os.remove for temp file cleanup
                with patch("os.path.exists", return_value=True), patch("os.remove"):
                    # Import main here to avoid early argparse initialization
                    from src.cli import main
                    await main()
        
        # Verify that convert_excel_to_python was called with force_evaluator=True
        mock_convert.assert_called_once()
        assert mock_convert.call_args[1].get('force_evaluator') == True

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_with_execution_error(self, mock_cli_upload, mock_convert, mock_argparse, mock_stderr):
        """Test the main function with script execution error."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.xlsx"
        mock_args.output = None
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.body = b"# Generated Python code"
        mock_convert.return_value = mock_response
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch execute_script_in_sandbox to simulate execution error
        error = subprocess.CalledProcessError(1, "python")
        error.output = b""
        error.stderr = b"Error"
        
        # Patch open to return actual bytes content
        with patch("builtins.open", mock_open):
            with patch("src.cli.execute_script_in_sandbox", side_effect=error):
                # Patch os.path.exists and os.remove for temp file cleanup
                with patch("os.path.exists", return_value=True), patch("os.remove"):
                    # Import main here to avoid early argparse initialization
                    from src.cli import main
                    with pytest.raises(SystemExit) as excinfo:
                        await main()
        
        # Verify that the program exited with an error code
        assert excinfo.value.code == 1
        
        # Check that an error message was printed to stderr
        assert "Script execution failed" in mock_stderr.getvalue()

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_with_timeout(self, mock_cli_upload, mock_convert, mock_argparse, mock_stderr):
        """Test the main function with script execution timeout."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.xlsx"
        mock_args.output = None
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.body = b"# Generated Python code"
        mock_convert.return_value = mock_response
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch execute_script_in_sandbox to simulate timeout
        with patch("builtins.open", mock_open):
            with patch("src.cli.execute_script_in_sandbox", side_effect=subprocess.TimeoutExpired("python", 5)):
                # Patch os.path.exists and os.remove for temp file cleanup
                with patch("os.path.exists", return_value=True), patch("os.remove"):
                    # Import main here to avoid early argparse initialization
                    from src.cli import main
                    with pytest.raises(SystemExit) as excinfo:
                        await main()
        
        # Verify that the program exited with an error code
        assert excinfo.value.code == 1
        
        # Check that an error message was printed to stderr
        assert "Script execution timed out" in mock_stderr.getvalue()

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    async def test_main_file_not_found(self, mock_argparse, mock_stderr):
        """Test the main function with file not found error."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "nonexistent.xlsx"
        mock_args.output = None
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Simulate file not found error
        with patch("builtins.open", side_effect=FileNotFoundError()):
            # Import main here to avoid early argparse initialization
            from src.cli import main
            with pytest.raises(SystemExit) as excinfo:
                await main()
        
        # Verify that the program exited with an error code
        assert excinfo.value.code == 1
        
        # Check that an error message was printed to stderr
        assert "Input file not found" in mock_stderr.getvalue()

    @pytest.mark.asyncio
    @patch("src.cli.argparse.ArgumentParser")
    @patch("src.cli.convert_excel_to_python")
    @patch("src.cli.CLIUploadFile")
    async def test_main_http_exception(self, mock_cli_upload, mock_convert, mock_argparse, mock_stderr):
        """Test the main function with HTTP exception."""
        # Setup mock ArgumentParser
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.input_file = "input.pdf"
        mock_args.output = None
        mock_args.force_evaluator = False
        mock_parser.parse_args.return_value = mock_args
        mock_argparse.return_value = mock_parser
        
        # Setup mock CLIUploadFile
        mock_upload_instance = MagicMock()
        mock_cli_upload.return_value = mock_upload_instance
        
        # Make convert_excel_to_python raise an HTTPException
        from fastapi import HTTPException
        mock_convert.side_effect = HTTPException(status_code=415, detail="Unsupported file type")
        
        # Patch open to return actual bytes content
        mock_file = MagicMock()
        mock_file.read.return_value = b"mock content"
        mock_open = MagicMock(return_value=mock_file)
        
        # Patch open to return actual bytes content
        with patch("builtins.open", mock_open):
            # Import main here to avoid early argparse initialization
            from src.cli import main
            with pytest.raises(SystemExit) as excinfo:
                await main()
        
        # Verify that the program exited with an error code
        assert excinfo.value.code == 1
        
        # Check that an error message was printed to stderr
        assert "Error processing file" in mock_stderr.getvalue()
        assert "Unsupported file type" in mock_stderr.getvalue() 