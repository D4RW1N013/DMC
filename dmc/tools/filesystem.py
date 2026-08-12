from pathlib import Path
import shutil
from ..models import Tool

def register(registry):
    def list_dir(path="."):
        p = Path(path).expanduser().resolve()
        return "\n".join(f"{x.name} [{ 'DIR' if x.is_dir() else 'FILE' }]" for x in p.iterdir())

    def read_file(path):
        return Path(path).expanduser().read_text(encoding="utf-8")

    def write_file(path, content):
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Wrote {p}"

    def create_directory(path):
        p = Path(path).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return f"Created {p}"

    def copy_file(source, destination):
        shutil.copy2(Path(source).expanduser(), Path(destination).expanduser())
        return f"Copied {source} -> {destination}"

    def move_file(source, destination):
        shutil.move(str(Path(source).expanduser()), str(Path(destination).expanduser()))
        return f"Moved {source} -> {destination}"

    def delete_path(path):
        p = Path(path).expanduser()
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"Deleted {p}"

    registry.register(Tool(
        "list_directory", "List files and folders in a directory.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        list_dir))

    registry.register(Tool(
        "read_file", "Read a UTF-8 text file.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        read_file))

    registry.register(Tool(
        "write_file", "Create or overwrite a UTF-8 text file.",
        {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
        write_file, "CONFIRM"))

    registry.register(Tool(
        "create_directory", "Create a directory.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        create_directory, "CONFIRM"))

    registry.register(Tool(
        "copy_file", "Copy a file.",
        {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["source", "destination"]},
        copy_file, "CONFIRM"))

    registry.register(Tool(
        "move_file", "Move a file.",
        {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["source", "destination"]},
        move_file, "CONFIRM"))

    registry.register(Tool(
        "delete_path", "Delete a file or directory. Potentially destructive.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        delete_path, "DANGEROUS"))
