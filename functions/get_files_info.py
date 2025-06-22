import os
    

def get_files_info(working_directory, directory=None):
    working_directory = os.path.abspath(working_directory)
    if directory == ".":
        directory = None
    if directory:
        if directory not in os.listdir(working_directory) or not ".":
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory or does not exist'
        working_directory = os.path.join(working_directory, directory)
    if not os.path.isdir(working_directory):
        return f'Error: "{directory}" is not a directory'
    files_info = []
    for file in os.listdir(working_directory):
        files_info.append(f"{file}: file_size= {os.path.getsize(os.path.join(working_directory, file))} bytes, is_dir={os.path.isdir(os.path.join(working_directory, file))}")
    files_info_string = "\n".join(files_info)
    return files_info_string

    