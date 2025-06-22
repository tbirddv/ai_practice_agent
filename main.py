import os
import sys
from dotenv import load_dotenv # type: ignore
from google import genai
from google.genai import types # type: ignore
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args
    args["working_directory"] = "./calculator"  # Inject the working directory automatically for security reasons
    available_functions = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }
    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f"Calling function: {function_name}")
    if function_name not in available_functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    result = available_functions[function_name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
                )
            ],
        )

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <prompt>")
        sys.exit(1)
    is_verbose = "--verbose" in sys.argv or "-v" in sys.argv
    user_args = [arg for arg in sys.argv[1:] if not arg.startswith("--") and not arg.startswith("-")]
    user_prompt = " ".join(user_args)
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read the content of a file
    - Write content to a file
    - Execute a Python file with optional arguments

    All paths you provide should be relative to the working directory which is './calculator'. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons. 
    For python files arguments are always optional, do not ask the user to provider them if missing.
    """
    if not user_prompt:
        print("Prompt cannot be empty.")
        sys.exit(1)
    if is_verbose:
        print(f"User prompt: {user_prompt}")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)]),]

    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                    ),
                },
            ),
        )
    
    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Retrieves the content of a specified file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to read, relative to the working directory.",
                ),
            }
        )
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Executes a python file with optional arguments, constrained to the working directory. If arguments are not provided do not ask the user for them, just run the file without arguments.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the python file to execute, relative to the working directory.",
                ),
                "args": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.STRING,
                        description="Arguments to pass to the python file. May be empty.",
                    ),
                ),
            }
        )
    )
    
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content to a specified file, constrained to the working directory. Will create the file if it does not exist, and will create any necessary directories.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to write, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content to write to the file.",
                ),
            }
        )
    )


    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )
    call_increment = 0
    while call_increment <= 20:
        call_increment += 1
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
                ),
            )
        if is_verbose:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        for candidate in response.candidates:
            messages.append(candidate.content)
        if response.function_calls:
            for function in response.function_calls:
                function_call = call_function(function, verbose=is_verbose)
                if not function_call.parts[0].function_response.response:
                    raise ValueError("Function call failed to return a response.")
                if is_verbose:
                    print(f"-> {function_call.parts[0].function_response.response}")
                messages.append(function_call)
        else:
            print(response.text)
            break



if __name__ == "__main__":
    main()