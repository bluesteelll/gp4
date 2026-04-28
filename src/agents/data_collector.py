from tools.file_tools import write_file
from tools.python_exec import python_exec
from tools.web_search import tavily_search

NAME = "data_collector"
MODEL = "claude-sonnet-4-6"
TOOLS = [write_file, python_exec, tavily_search]
