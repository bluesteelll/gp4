from tools.file_tools import write_file
from tools.python_exec import python_exec

NAME = "data_collector"
MODEL = "gpt-4.1-mini"
TOOLS = [write_file, python_exec]
