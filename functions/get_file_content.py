import os


def get_file_content(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_directory + os.sep):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    MAX_CHARACTERS = 10000
    if os.path.getsize(abs_file_path) > MAX_CHARACTERS:
        truncation_message = f'[...File "{file_path}" truncated at {MAX_CHARACTERS} characters]'
    else:
        truncation_message = None
    try:
        with open(abs_file_path, 'r', encoding='utf-8') as file:
            content = file.read(MAX_CHARACTERS)
    except Exception as e:
        return f'Error reading file "{file_path}": {str(e)}'
    if truncation_message:
        content += truncation_message
    return content if content else f'Error: File "{file_path}" is empty or could not be read.'