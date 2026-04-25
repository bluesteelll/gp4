import subprocess
import sys
import tempfile
from pathlib import Path

from langchain_core.tools import tool


@tool
def python_exec(code):
    """Execute Python code in an isolated subprocess with a 60-second timeout. Returns stdout, stderr, and returncode."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 60s"}
    finally:
        Path(script_path).unlink(missing_ok=True)
