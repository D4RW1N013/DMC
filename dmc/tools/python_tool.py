import subprocess
import sys
from ..models import Tool

def register(registry):
    def run_python(code):
        p = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return f"EXIT CODE: {p.returncode}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"

    registry.register(Tool(
        "run_python",
        "Execute a short Python program using the same Python environment as DMC.",
        {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
        run_python, "CONFIRM"))
