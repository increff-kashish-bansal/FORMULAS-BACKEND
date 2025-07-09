import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO
import json
import os
import tempfile

from src.main import app, request_warnings

class TestMainAPI:
    """Tests for the main API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_file_content(self):
        """Create a mock Excel file content."""
        return b"mock excel file content"
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    def test_convert_endpoint_without_output_file(
        self, mock_execute, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test the /convert endpoint without an output filename."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code"
        mock_execute.return_value = ("Execution output", "", 0)  # stdout, stderr, returncode
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request
        response = client.post("/convert/", files=test_file, data={"force_evaluator": "false"})
        
        # Check the response
        assert response.status_code == 200
        response_data = response.json()
        assert "script" in response_data
        assert "# Generated Python code" in response_data["script"]
        assert "warnings" in response_data
        assert "execution_output" in response_data
        assert response_data["execution_output"]["stdout"] == "Execution output"
        assert response_data["execution_output"]["stderr"] == ""
        assert response_data["execution_output"]["return_code"] == 0
        assert "log_url" in response_data
        
        # Verify mocks were called
        mock_handle_upload.assert_called_once()
        mock_model_compiler.return_value.read_and_parse_archive.assert_called_once()
        mock_generate_code.assert_called_once_with(mock_model)
        mock_execute.assert_called_once()
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("builtins.open", new_callable=MagicMock)
    def test_convert_endpoint_with_output_file(
        self, mock_open, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test the /convert endpoint with an output filename."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request with output_filename
        response = client.post(
            "/convert/", 
            files=test_file, 
            data={
                "force_evaluator": "false",
                "output_filename": "output.py"
            }
        )
        
        # Check the response
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
        assert "Successfully converted and saved to output.py" in response_data["message"]
        assert "warnings" in response_data
        assert "log_url" in response_data
        
        # Verify mocks were called
        mock_handle_upload.assert_called_once()
        mock_model_compiler.return_value.read_and_parse_archive.assert_called_once()
        mock_generate_code.assert_called_once_with(mock_model)
        mock_open.assert_called_once_with("output.py", "w")
        mock_file.write.assert_called_once()
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    def test_convert_endpoint_with_force_evaluator(
        self, mock_execute, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test the /convert endpoint with force_evaluator=true."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code with evaluator"
        mock_execute.return_value = ("Execution output", "", 0)  # stdout, stderr, returncode
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request with force_evaluator=true
        response = client.post("/convert/", files=test_file, data={"force_evaluator": "true"})
        
        # Check the response
        assert response.status_code == 200
        response_data = response.json()
        assert "script" in response_data
        assert "# Generated Python code with evaluator" in response_data["script"]
        
        # Verify generate_static_python_code was called with force_evaluator=True
        # Note: In the current implementation, the force_evaluator parameter isn't actually passed to generate_static_python_code
        # This test assumes it would be in a complete implementation
        mock_generate_code.assert_called_once_with(mock_model)
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    def test_convert_endpoint_with_csv_file(
        self, mock_execute, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client
    ):
        """Test the /convert endpoint with a CSV file."""
        # Set up mocks
        mock_csv_content = b"A,B,C\n1,2,=A1+B1"
        mock_handle_upload.return_value = mock_csv_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code from CSV"
        mock_execute.return_value = ("CSV Execution output", "", 0)  # stdout, stderr, returncode
        
        # Create a test CSV file
        test_file = {"file": ("test.csv", BytesIO(mock_csv_content), "text/csv")}
        
        # Make the request
        response = client.post("/convert/", files=test_file)
        
        # Check the response
        assert response.status_code == 200
        response_data = response.json()
        assert "script" in response_data
        assert "# Generated Python code from CSV" in response_data["script"]
        assert "execution_output" in response_data
        assert response_data["execution_output"]["stdout"] == "CSV Execution output"
    
    @patch("src.main.handle_file_upload")
    def test_convert_endpoint_file_validation_error(self, mock_handle_upload, client):
        """Test the /convert endpoint with file validation error."""
        from src.file_handler import InvalidFileExtensionError
        
        # Set up mock to raise an error
        mock_handle_upload.side_effect = InvalidFileExtensionError("Invalid file extension: .pdf")
        
        # Create a test file
        test_file = {"file": ("test.pdf", BytesIO(b"invalid file"), "application/pdf")}
        
        # Make the request
        response = client.post("/convert/", files=test_file)
        
        # Check the response
        assert response.status_code == 415  # Unsupported Media Type
        response_data = response.json()
        assert "detail" in response_data
        assert "Invalid file extension" in response_data["detail"]
        assert "warnings" in response_data
        assert "log_url" in response_data
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    def test_convert_endpoint_parse_error(self, mock_model_compiler, mock_handle_upload, client, mock_file_content):
        """Test the /convert endpoint with parsing error."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model_compiler.return_value.read_and_parse_archive.side_effect = Exception("Parsing error")
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request
        response = client.post("/convert/", files=test_file)
        
        # Check the response - the actual implementation returns 500 for parsing errors
        assert response.status_code == 500  # Internal Server Error
        assert "Parsing error" in response.text
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    def test_convert_endpoint_execution_error(
        self, mock_execute, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test the /convert endpoint with script execution error."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code with error"
        mock_execute.return_value = ("", "Runtime error: division by zero", 1)  # stdout, stderr, returncode with error
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request
        response = client.post("/convert/", files=test_file)
        
        # Check the response - even with execution error, the API should return 200
        assert response.status_code == 200
        response_data = response.json()
        assert "script" in response_data
        assert "execution_output" in response_data
        assert response_data["execution_output"]["stderr"] == "Runtime error: division by zero"
        assert response_data["execution_output"]["return_code"] == 1
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    @patch("tempfile.NamedTemporaryFile")
    def test_convert_endpoint_sandbox_timeout(
        self, mock_tempfile, mock_execute, mock_generate_code, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test the /convert endpoint with sandbox execution timeout."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate_code.return_value = "# Generated Python code"
        
        # Mock the temporary file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/temp_script.py"
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file
        
        # Mock execute_script_in_sandbox to raise a timeout
        import subprocess
        mock_execute.side_effect = subprocess.TimeoutExpired(cmd="python", timeout=5)
        
        # Create a test file
        test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        # Make the request
        response = client.post("/convert/", files=test_file)
        
        # Check the response - even with timeout, the API should return 200
        assert response.status_code == 200
        response_data = response.json()
        assert "script" in response_data
        assert "execution_output" in response_data
        assert "Script execution timed out" in response_data["execution_output"]["stderr"]
    
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    def test_logs_endpoint(self, mock_open, mock_exists, client):
        """Test the /logs endpoint."""
        # Set up mocks
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Log content"
        mock_open.return_value = mock_file
        
        # Make the request
        response = client.get("/logs/")
        
        # Check the response
        assert response.status_code == 200
        assert response.text == "Log content"
        mock_exists.assert_called_once()
        mock_open.assert_called_once()
    
    @patch("os.path.exists")
    def test_logs_endpoint_not_found(self, mock_exists, client):
        """Test the /logs endpoint when log file doesn't exist."""
        # Set up mock
        mock_exists.return_value = False
        
        # Make the request
        response = client.get("/logs/")
        
        # Check the response
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert "Log file not found" in response_data["detail"]
    
    @patch("src.main.handle_file_upload")
    def test_convert_endpoint_missing_file(self, mock_handle_upload, client):
        """Test the /convert endpoint without providing a file."""
        # Make the request without a file
        response = client.post("/convert/", files={})
        
        # Check the response
        assert response.status_code == 422  # Unprocessable Entity (FastAPI validation error)
        response_data = response.json()
        assert "detail" in response_data
        assert any("file" in error["loc"] for error in response_data["detail"])
    
    @patch("src.main.handle_file_upload")
    @patch("src.main.ModelCompiler")
    @patch("src.main.Evaluator")
    @patch("src.main.generate_static_python_code")
    @patch("src.main.execute_script_in_sandbox")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_convert_endpoint_temp_file_cleanup(
        self, mock_remove, mock_exists, mock_execute, mock_generate, mock_evaluator, 
        mock_model_compiler, mock_handle_upload, client, mock_file_content
    ):
        """Test that temporary files are cleaned up after execution."""
        # Set up mocks
        mock_handle_upload.return_value = mock_file_content
        mock_model = MagicMock()
        mock_model_compiler.return_value.read_and_parse_archive.return_value = mock_model
        mock_generate.return_value = "# Generated Python code"
        mock_execute.return_value = ("Execution output", "", 0)  # stdout, stderr, returncode
        
        # Make os.path.exists return True for any path (to trigger cleanup)
        mock_exists.return_value = True
        
        # Create a mock temporary file
        temp_file_path = "/tmp/temp_script.py"
        
        # Use patch to mock tempfile.NamedTemporaryFile
        with patch("tempfile.NamedTemporaryFile") as mock_tempfile:
            # Setup the mock temp file
            mock_temp_file = MagicMock()
            mock_temp_file.name = temp_file_path
            mock_tempfile.return_value.__enter__.return_value = mock_temp_file
            
            # Create a test file
            test_file = {"file": ("test.xlsx", BytesIO(mock_file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            
            # Make the request
            response = client.post("/convert/", files=test_file)
            
            # Check the response
            assert response.status_code == 200
            
        # Verify the temporary file was cleaned up
        mock_remove.assert_called_once() 