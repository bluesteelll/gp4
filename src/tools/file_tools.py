from pathlib import Path

from langchain_core.tools import tool


@tool
def read_file(path):
    """Read a text file at the given path and return its contents."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@tool
def write_file(path, content):
    """Write text content to a file, creating parent directories if needed. Returns the absolute path."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return str(p.resolve())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@tool
def list_files(path):
    """List files and directories directly inside the given path. Returns a list of names."""
    try:
        return [p.name for p in Path(path).iterdir()]
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
