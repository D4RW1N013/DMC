import json
from pathlib import Path
from datetime import datetime


class Memory:

    def __init__(self, path: Path):

        self.path = path

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.path.exists():

            self._save({
                "facts": [],
                "events": []
            })

    # =========================================================
    # LOAD
    # =========================================================

    def _load(self):

        try:

            return json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return {
                "facts": [],
                "events": []
            }

    # =========================================================
    # SAVE
    # =========================================================

    def _save(self, data):

        self.path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    # =========================================================
    # FACTS
    # =========================================================

    def remember(self, text: str):

        data = self._load()

        data["facts"].append({
            "text": text,
            "created": datetime.now().isoformat()
        })

        self._save(data)

    # =========================================================
    # EVENTS
    # =========================================================

    def add_event(self, text: str):

        data = self._load()

        data["events"].append({
            "text": text,
            "created": datetime.now().isoformat()
        })

        # Wir behalten die Events weiterhin.
        #
        # ABER:
        # Sie werden NICHT mehr automatisch
        # an das LLM geschickt.

        data["events"] = data["events"][-200:]

        self._save(data)

    # =========================================================
    # CONTEXT
    # =========================================================

    def context(self, limit=20):

        data = self._load()

        facts = data.get(
            "facts",
            []
        )[-limit:]

        lines = [
            "KNOWN USER FACTS:"
        ]

        for fact in facts:

            lines.append(
                f"- {fact['text']}"
            )

        if not facts:

            lines.append(
                "- No persistent user facts are known."
            )

        return "\n".join(lines)

    # =========================================================
    # DEBUG / HISTORY
    # =========================================================

    def recent_events(self, limit=20):

        data = self._load()

        return data.get(
            "events",
            []
        )[-limit:]