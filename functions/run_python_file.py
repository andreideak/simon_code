import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=None):

    try:
        work_dir_abs = os.path.abspath(working_directory)
        file_path_abs = os.path.normpath(os.path.join(work_dir_abs,file_path))
        in_work_dir = os.path.commonpath([work_dir_abs,file_path_abs]) == work_dir_abs

        if not in_work_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        
        if not os.path.isfile(file_path_abs):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", file_path_abs]
        if args != None:
            command.extend(args)

        
        completed_process = subprocess.run(
            command,
            capture_output=True,
            cwd=work_dir_abs,
            timeout=30.0,
            text=True
        )

        output_message = []

        if completed_process.returncode != 0:
            output_message.append(f"Process exited with code {completed_process.returncode}")

        if len(completed_process.stdout) == 0 and len(completed_process.stderr) == 0:
            output_message.append("No output produced")

        if len(completed_process.stderr) != 0:
            output_message.append(f"STDERR: {completed_process.stderr}")

        if len(completed_process.stdout) != 0:
            output_message.append(f"STDOUT: {completed_process.stdout}")

        return "\n".join(output_message)

    except Exception as e:
        return f"Error: executing Python file: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python (.py) file from the working directory",
    parameters=types.Schema(
        required=["file_path"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the Python (.py) file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="Command arguments to use when executing the Python file (default is None)",
            ),
        },
    ),
)