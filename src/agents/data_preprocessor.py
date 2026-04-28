from tools.file_tools import list_files, read_file, write_file
from tools.python_exec import python_exec

NAME = "data_preprocessor"
MODEL = "gemini-3.1-pro-preview"
TOOLS = [read_file, write_file, list_files, python_exec]
