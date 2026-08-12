from pathlib import Path
from ..models import Tool

def register(registry):
    def inspect_project(folder, max_files=200):
        root = Path(folder).expanduser().resolve()
        if not root.exists():
            return f"Folder does not exist: {root}"
        rows = []
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(root)
                if any(part in {".git", ".venv", "venv", "__pycache__", "node_modules"} for part in rel.parts):
                    continue
                try:
                    size = p.stat().st_size
                except OSError:
                    size = -1
                rows.append(f"{rel} ({size} bytes)")
                if len(rows) >= max_files:
                    break
        return f"PROJECT: {root}\nFILES:\n" + "\n".join(rows)

    registry.register(Tool(
        "inspect_project",
        "Inspect a project folder and list relevant files while skipping common generated folders.",
        {
            "type": "object",
            "properties": {
                "folder": {"type": "string"},
                "max_files": {"type": "integer", "minimum": 1, "maximum": 500}
            },
            "required": ["folder"]
        },
        inspect_project
    ))
