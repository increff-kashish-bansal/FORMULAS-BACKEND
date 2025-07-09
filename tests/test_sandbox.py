import pytest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
import resource

from src.sandbox import execute_script_in_sandbox, set_resource_limits, MAX_CPU_TIME, MAX_MEMORY_BYTES

class TestSandbox:
    """Tests for the sandbox execution functionality."""
    
    @patch('src.sandbox.set_resource_limits')  # Patch the resource limits function
    def test_execute_valid_script(self, mock_set_limits):
        """Test executing a valid script in the sandbox."""
        # Create a temporary script file with valid Python code
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
            temp_file.write('print("Hello, sandbox!")')
            script_path = temp_file.name
        
        try:
            # Execute the script in the sandbox
            stdout, stderr, returncode = execute_script_in_sandbox(script_path)
            
            # Check the results
            assert "Hello, sandbox!" in stdout
            assert stderr == ""
            assert returncode == 0
        finally:
            # Clean up
            if os.path.exists(script_path):
                os.remove(script_path)
    
    @patch('src.sandbox.set_resource_limits')  # Patch the resource limits function
    def test_execute_script_with_error(self, mock_set_limits):
        """Test executing a script with syntax error in the sandbox."""
        # Create a temporary script file with invalid Python code
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
            temp_file.write('print("Incomplete string')  # Missing closing quote
            script_path = temp_file.name
        
        try:
            # Execute the script in the sandbox and expect a non-zero return code
            with pytest.raises(subprocess.CalledProcessError):
                execute_script_in_sandbox(script_path)
        finally:
            # Clean up
            if os.path.exists(script_path):
                os.remove(script_path)
    
    @patch('resource.setrlimit')
    def test_set_resource_limits(self, mock_setrlimit):
        """Test that resource limits are set correctly."""
        # Call the function
        set_resource_limits()
        
        # Check that setrlimit was called with the expected arguments
        mock_setrlimit.assert_any_call(resource.RLIMIT_CPU, (MAX_CPU_TIME, MAX_CPU_TIME))
        mock_setrlimit.assert_any_call(resource.RLIMIT_DATA, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
    
    @patch('src.sandbox.set_resource_limits')  # Patch the resource limits function
    def test_execute_script_timeout(self, mock_set_limits):
        """Test that a script that runs too long raises a TimeoutExpired exception."""
        # Create a temporary script with an infinite loop
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
            temp_file.write('import time\nwhile True: time.sleep(1)')
            script_path = temp_file.name
        
        try:
            # Execute with a very short timeout
            with pytest.raises(subprocess.TimeoutExpired):
                execute_script_in_sandbox(script_path, timeout=1)
        finally:
            # Clean up
            if os.path.exists(script_path):
                os.remove(script_path) 