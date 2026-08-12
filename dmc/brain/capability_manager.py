import json
from pathlib import Path


class CapabilityManager:

    def __init__(
        self,
        llm,
        registry,
        settings,
        event_callback=None
    ):
        self.llm = llm
        self.registry = registry
        self.settings = settings

        self.event_callback = (
            event_callback or
            (lambda message: None)
        )

        self.root = (
            Path(settings.workspace)
            / "capabilities"
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )

    def inspect_gap(
        self,
        user_text,
        missing_capability
    ):

        self.event_callback(
            "Capability Manager: "
            "capability gap detected"
        )

        self.event_callback(
            f"Capability Manager: "
            f"missing = {missing_capability}"
        )

        return {
            "status": "missing",
            "capability":
                missing_capability,
            "research_required": True,
            "safe_to_auto_build": False
        }

    def list_learned(self):

        capabilities = []

        if not self.root.exists():
            return capabilities

        for path in self.root.iterdir():

            if not path.is_dir():
                continue

            metadata = (
                path / "capability.json"
            )

            if not metadata.exists():
                continue

            try:

                data = json.loads(
                    metadata.read_text(
                        encoding="utf-8"
                    )
                )

                capabilities.append(data)

            except Exception:
                continue

        return capabilities

    def remember_capability(
        self,
        name,
        description,
        implementation=""
    ):

        safe_name = "".join(
            character
            if (
                character.isalnum()
                or character in "_-"
            )
            else "_"
            for character in name.lower()
        ).strip("_")

        capability_dir = (
            self.root / safe_name
        )

        capability_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        metadata = {
            "name": name,
            "description": description,
            "implementation": implementation,
            "status": "learned"
        }

        (
            capability_dir /
            "capability.json"
        ).write_text(
            json.dumps(
                metadata,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return capability_dir
