import json


class Executor:

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

    def execute(
        self,
        user_text,
        plan,
        context=""
    ):

        results = []

        steps = plan.get("steps", [])

        for index, step in enumerate(steps, start=1):

            objective = step.get(
                "objective",
                ""
            )

            self.event_callback(
                f"Brain: executing step "
                f"{index}/{len(steps)}: {objective}"
            )

            result = self._execute_step(
                user_text,
                objective,
                step,
                context
            )

            results.append(result)

            if result.get("status") == "error":
                break

        return results

    def _execute_step(
        self,
        user_text,
        objective,
        step,
        context
    ):

        preferred_tools = step.get(
            "preferred_tools",
            []
        )

        available_tools = self.registry.schemas()

        selected_tools = []

        for tool in available_tools:

            function = tool.get(
                "function",
                {}
            )

            name = function.get("name")

            if (
                not preferred_tools
                or name in preferred_tools
            ):
                selected_tools.append(tool)

        prompt = f"""
You are DMC's execution engine.

Execute ONE concrete step of the plan.

USER REQUEST:
{user_text}

CURRENT STEP:
{objective}

VERIFICATION:
{step.get("verification", "")}

CONTEXT:
{context}

AVAILABLE TOOLS:
Use the supplied tools.

Rules:

- Actually perform the requested action.
- Do not merely explain how to do it.
- Do not perform unrelated actions.
- Inspect tool results.
- Never claim success without evidence.
"""

        try:

            msg = self.llm.chat(
                [
                    {
                        "role": "system",
                        "content": prompt
                    }
                ],
                selected_tools
            )

        except Exception as exc:

            return {
                "status": "error",
                "objective": objective,
                "error":
                    f"{type(exc).__name__}: {exc}"
            }

        tool_calls = (
            msg.get("tool_calls") or []
        )

        content = (
            msg.get("content") or ""
        )

        if not tool_calls:

            return {
                "status": "completed",
                "objective": objective,
                "content": content
            }

        tool_results = []

        for call in tool_calls:

            function = call.get(
                "function",
                {}
            )

            name = function.get("name")

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

                tool_results.append({
                    "tool": name,
                    "status": "error",
                    "result":
                        "Invalid JSON arguments"
                })

                continue

            tool = self.registry.get(name)

            if not tool:

                tool_results.append({
                    "tool": name,
                    "status": "error",
                    "result":
                        f"Unknown tool: {name}"
                })

                continue

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

                    tool_results.append({
                        "tool": name,
                        "status": "cancelled",
                        "result":
                            "ACTION CANCELLED BY USER"
                    })

                    continue

            try:

                self.event_callback(
                    f"Executing: {name}"
                )

                result = tool.handler(
                    **args
                )

                self.event_callback(
                    f"Finished: {name}"
                )

                tool_results.append({
                    "tool": name,
                    "status": "success",
                    "result": str(result)
                })

            except Exception as exc:

                self.event_callback(
                    f"Tool failed: {name}"
                )

                tool_results.append({
                    "tool": name,
                    "status": "error",
                    "result":
                        f"{type(exc).__name__}: {exc}"
                })

        return {
            "status": "completed",
            "objective": objective,
            "content": content,
            "tools": tool_results
        }
