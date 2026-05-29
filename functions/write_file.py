import os
from google.genai import types

def write_file(working_directory, file_path, content):
    error = ""
    try:

        # Check if valid file
        working_dir_abs = os.path.abspath(working_directory)
        file_path_abs = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, file_path_abs]) == working_dir_abs

        # Check if file exists in working directory
        if not valid_target_file:
            error = f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
            return error
        
        # Check if file is actually a directory
        is_directory = os.path.isdir(file_path_abs)
        if is_directory:
            error = f'Error: Cannot write to "{file_path}" as it is a directory'
            return error
        
        # Create any missing directories in the path
        parent_path = os.path.dirname(file_path_abs)
        os.makedirs(name=parent_path,exist_ok=True)

        # Write content to file
        with open(file_path_abs, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except:
        return error


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write to a file in a specific directory, relative to the working directory",
    parameters=types.Schema(
        required=[],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path of the file to write into, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="String content to write into the file",
            ),
        },
    ),
)