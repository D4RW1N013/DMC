from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]
    risk: str = "SAFE"  # SAFE | CONFIRM | DANGEROUS

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
