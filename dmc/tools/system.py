import platform
import psutil
from ..models import Tool

def register(registry):
    def system_info():
        return (
            f"OS: {platform.platform()}\n"
            f"Machine: {platform.machine()}\n"
            f"CPU: {platform.processor()}\n"
            f"CPU usage: {psutil.cpu_percent(interval=0.5)}%\n"
            f"RAM: {psutil.virtual_memory().percent}% used\n"
            f"Disk: {psutil.disk_usage('/').percent}% used"
        )

    def process_list():
        rows = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                rows.append(p.info)
            except Exception:
                pass
        rows.sort(key=lambda x: x.get("memory_percent") or 0, reverse=True)
        return "\n".join(str(x) for x in rows[:30])

    registry.register(Tool(
        "system_info", "Get basic operating-system, CPU, RAM and disk information.",
        {"type": "object", "properties": {}}, system_info))

    registry.register(Tool(
        "process_list", "List the top processes by memory usage.",
        {"type": "object", "properties": {}}, process_list))
