from tools.file_tools import list_files, read_file, write_file
from tools.python_exec import python_exec

NAME = "model_reviser"
MODEL = "claude-opus-4-7-think"
TOOLS = [read_file, write_file, list_files, python_exec]
