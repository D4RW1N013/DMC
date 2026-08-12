import json


class FastPath:

    def __init__(
        self,
        llm,
        registry,
        settings,
        event_callback=None,
        confirm_callback=None
    ):
        self.llm = llm
        self.registry = registry
        self.settings = settings
        self.event_callback = (
            event_callback or
            (lambda message: None)
        )
        self.confirm_callback = (
            confirm_callback or
            (lambda tool, args: True)
        )

    def run(
        self,
        user_text,
        user_name="",
        language="de"
    ):

        self.event_callback(
            "FastPath: processing simple request"
        )

        messages = [
            {
                "role": "system",
                "content": f"""
You are DMC, a local computer assistant.

The user is making a simple request.

User name:
{user_name or "not provided"}

Preferred language:
{language}

Answer naturally in the requested language.

If the request requires a tool, use exactly the
appropriate available tool.

Do not use unnecessary tools.

Do not perform unrelated actions.

Do not claim an action succeeded unless the tool
actually reports success.
"""
            },
            {
                "role": "user",
                "content": user_text
            }
        ]

        try:

            response = self.llm.chat(
                messages,
                self.registry.schemas()
            )

        except Exception as exc:

            return (
                f"FastPath error: "
                f"{type(exc).__name__}: {exc}"
            )

        tool_calls = (
            response.get("tool_calls")
            or []
        )

        content = (
            response.get("content")
            or ""
        )

        # ---------------------------------------------
        # Normal conversation
        # ---------------------------------------------

        if not tool_calls:

            return content.strip()

        # ---------------------------------------------
        # Execute simple tool call
        # ---------------------------------------------

        tool_results = []

        for call in tool_calls:

            function = call.get(
                "function",
                {}
            )

            name = function.get(
                "name"
            )

            raw_args = function.get(
                "arguments",
                {}
            )

            try:

                args = (
                    json.loads(raw_args)
                    if isinstance(raw_args, str)
                    else raw_args
                )

            except json.JSONDecodeError:

                return (
                    "DMC konnte die "
                    "Tool-Argumente nicht "
                    "verarbeiten."
                )

            tool = self.registry.get(
                name
            )

            if not tool:

                return (
                    f"DMC kennt das Tool "
                    f"'{name}' nicht."
                )

            if (
                tool.risk in {
                    "CONFIRM",
                    "DANGEROUS"
                }
                and
                self.settings.require_confirmation
            ):

                allowed = self.confirm_callback(
                    tool,
                    args
                )

                if not allowed:

                    return (
                        "Die Aktion wurde "
                        "abgebrochen."
                    )

            try:

                self.event_callback(
                    f"FastPath: executing {name}"
                )

                result = tool.handler(
                    **args
                )

                self.event_callback(
                    f"FastPath: finished {name}"
                )

                tool_results.append({
                    "tool": name,
                    "result": str(result)
                })

            except Exception as exc:

                return (
                    f"Tool '{name}' ist "
                    f"fehlgeschlagen: "
                    f"{type(exc).__name__}: {exc}"
                )

        # ---------------------------------------------
        # One final LLM call to formulate the answer
        # ---------------------------------------------

        final_messages = [
            {
                "role": "system",
                "content": f"""
You are DMC.

Answer the user naturally in language:
{language}

Use ONLY the actual tool results below.

Do not invent information.

Do not claim that additional tests were performed.

Keep the answer concise.
"""
            },
            {
                "role": "user",
                "content": user_text
            },
            {
                "role": "tool",
                "content": json.dumps(
                    tool_results,
                    ensure_ascii=False
                )
            }
        ]

        try:

            final = self.llm.chat(
                final_messages
            )

            return (
                final.get("content")
                or str(tool_results)
            ).strip()

        except Exception:

            return str(
                tool_results
            )
