import json


class Reflector:

    def __init__(
        self,
        llm,
        settings,
        event_callback=None
    ):
        self.llm = llm
        self.settings = settings
        self.event_callback = (
            event_callback or
            (lambda message: None)
        )

    def reflect(
        self,
        user_text,
        plan,
        execution_results,
        observation
    ):

        self.event_callback(
            "Brain: reflecting on failure"
        )

        prompt = f"""
You are DMC's reflection engine.

The task was not successfully verified.

Determine what actually went wrong and what
DMC should do next.

USER REQUEST:
{user_text}

PLAN:
{json.dumps(plan, indent=2)}

EXECUTION RESULTS:
{json.dumps(execution_results, indent=2)}

VERIFICATION:
{json.dumps(observation, indent=2)}

Return ONLY valid JSON:

{{
    "diagnosis": "actual reason for failure",
    "recoverable": true,
    "capability_missing": false,
    "missing_capability": "",
    "next_strategy": "what DMC should try next",
    "retry": true
}}

Rules:

- Do not invent causes.
- Use actual evidence.
- Do not repeat a failed approach without a reason.
- If a required capability is missing, say so.
"""

        try:

            response = self.llm.chat([
                {
                    "role": "system",
                    "content":
                        "You are DMC's reflection "
                        "engine. Return JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ])

            content = (
                response.get("content") or ""
            ).strip()

            result = self._parse(content)

            if result:
                return result

        except Exception as exc:

            return {
                "diagnosis":
                    f"Reflection failed: "
                    f"{type(exc).__name__}: {exc}",
                "recoverable": False,
                "capability_missing": False,
                "missing_capability": "",
                "next_strategy": "",
                "retry": False
            }

        return {
            "diagnosis":
                "Unable to determine failure.",
            "recoverable": False,
            "capability_missing": False,
            "missing_capability": "",
            "next_strategy": "",
            "retry": False
        }

    @staticmethod
    def _parse(content):

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        if "```" in content:

            for part in content.split("```"):

                cleaned = part.strip()

                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue

        return None
