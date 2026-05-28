import os

# LLM Guardrail: we never want it to be able to perform any work outside the working_directory that we give it.
# Without this restriction, the LLM might run amok anywhere on the machine, reading sensitive files or overwriting important data. 
# This is a very important step that we'll bake into every function the LLM can call.

def get_files_info(working_directory, directory="."):
    try:
        error = ""
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = os.path.commonpath([target_dir, working_dir_abs]) == working_dir_abs

        if not valid_target_dir:
            error = f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
            return error
        
        if not os.path.isdir(target_dir):
            error = f'Error: "{directory}" is not a directory'
            return error
        
        files = os.listdir(target_dir)
        file_info = ""
        for file in files:
            size = os.path.getsize(f"{target_dir}/{file}")
            is_dir = os.path.isdir(f"{target_dir}/{file}")
            file_info += f"- {file}: file_size={size} bytes, is_dir={is_dir}\n"
        return file_info
    except:
        return error