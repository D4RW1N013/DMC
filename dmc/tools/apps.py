import platform
import subprocess
import shutil
from ..models import Tool

def register(registry):
    def open_application(name):
        system = platform.system()
        if system == "Windows":
            p = subprocess.Popen(["cmd", "/c", "start", "", name])
        elif system == "Darwin":
            p = subprocess.Popen(["open", "-a", name])
        else:
            if not shutil.which(name):
                return f"Application not found in PATH: {name}"
            p = subprocess.Popen([name])
        return f"Started {name} (pid={p.pid})"

    registry.register(Tool(
        "open_application",
        "Open an installed application by name.",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        open_application, "CONFIRM"))
