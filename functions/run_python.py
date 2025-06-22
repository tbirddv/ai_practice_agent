import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_directory + os.sep):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory.'
    
    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    
    if not abs_file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        if args:
            command = ['python3', abs_file_path] + args
        else:
            command = ['python3', abs_file_path]
        output = subprocess.run(
            command,
            cwd=abs_working_directory,
            capture_output=True,
            text=True,
            check=True,
            timeout=30)
        if not output.stdout and not output.stderr:
            return f'No output produced.'
        return f'STDOUT: {output.stdout} \nSTDERR: {output.stderr}'
    except subprocess.CalledProcessError as e:
        return f'Process exited with code {e.returncode}. \nSTDOUT: {e.stdout} \nSTDERR: {e.stderr}'
    except subprocess.TimeoutExpired as e:
        return f'Error: Execution of "{file_path}" timed out after {e.timeout} seconds.'
    except Exception as e:
        return f'Error: {str(e)}.'