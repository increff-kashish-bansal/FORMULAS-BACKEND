import os
import sys
import resource
import subprocess
import logging

# Define resource limits
MAX_CPU_TIME = 30  # seconds
MAX_MEMORY_BYTES = 100 * 1024 * 1024  # 100 MB

logger = logging.getLogger(__name__)

def set_resource_limits():
    """
    Set resource limits for the process to prevent runaway scripts.
    
    This function sets CPU time and memory limits to prevent scripts
    from consuming excessive resources.
    """
    try:
        # Set CPU time limit (RLIMIT_CPU)
        resource.setrlimit(resource.RLIMIT_CPU, (MAX_CPU_TIME, MAX_CPU_TIME))
        
        # Set memory limit (RLIMIT_DATA for heap)
        resource.setrlimit(resource.RLIMIT_DATA, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))
        
        return True
    except Exception as e:
        # Log the error but don't fail - this allows tests to run without setting limits
        sys.stderr.write(f"Error setting resource limits: {e}\n")
        return False

def execute_script_in_sandbox(script_path: str, timeout: int = 30):
    """
    Executes a Python script in a sandboxed subprocess.

    Args:
        script_path (str): The path to the Python script to execute.
        timeout (int): The maximum time (in seconds) the script is allowed to run.

    Returns:
        tuple: A tuple containing (stdout, stderr, returncode).

    Raises:
        subprocess.TimeoutExpired: If the script execution exceeds the timeout.
        subprocess.CalledProcessError: If the script returns a non-zero exit code.
        RuntimeError: For any unexpected errors during script execution.
    """
    process = None # Initialize process to None
    try:
        # Using sys.executable to ensure the current Python interpreter is used
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # Capture stdout/stderr as text (decoded) for easier handling
            preexec_fn=set_resource_limits # Set resource limits in the child process
        )

        stdout, stderr = process.communicate(timeout=timeout)
        returncode = process.returncode

        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, process.args, output=stdout, stderr=stderr)

        return stdout, stderr, returncode
    except subprocess.TimeoutExpired:
        if process:
            process.kill() # Kill the process if it timed out
            process.wait() # Wait for the process to terminate
        raise # Re-raise the TimeoutExpired exception
    except subprocess.CalledProcessError:
        raise # Re-raise the CalledProcessError to indicate a script error
    except Exception as e:
        # Catch any other unexpected errors
        raise RuntimeError(f"Failed to execute script in sandbox: {e}") 