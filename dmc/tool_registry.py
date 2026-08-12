from .models import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def all(self):
        return list(self._tools.values())

    def schemas(self):
        return [t.schema() for t in self.all()]
