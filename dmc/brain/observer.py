import json


class Observer:

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

    def verify(
        self,
        user_text,
        plan,
        execution_results
    ):

        self.event_callback(
            "Brain: verifying result"
        )

        prompt = f"""
You are DMC's verification engine.

Determine whether the user's task was ACTUALLY completed.

USER REQUEST:
{user_text}

PLAN:
{json.dumps(plan, indent=2)}

EXECUTION RESULTS:
{json.dumps(execution_results, indent=2)}

Do not assume success.

Only mark success if the evidence proves it.

Return ONLY valid JSON:

{{
    "success": true,
    "confidence": 0.0,
    "reason": "why the evidence proves success or failure",
    "failed_step": "",
    "needs_retry": false,
    "recommended_action": ""
}}
"""

        try:

            response = self.llm.chat([
                {
                    "role": "system",
                    "content":
                        "You are DMC's verification "
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
                "success": False,
                "confidence": 0.0,
                "reason":
                    f"Verification failed: "
                    f"{type(exc).__name__}: {exc}",
                "failed_step": "",
                "needs_retry": True,
                "recommended_action":
                    "Inspect the result again."
            }

        return {
            "success": False,
            "confidence": 0.0,
            "reason":
                "Could not verify result.",
            "failed_step": "",
            "needs_retry": True,
            "recommended_action":
                "Inspect the result again."
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
