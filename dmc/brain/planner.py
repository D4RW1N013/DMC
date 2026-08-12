import json


class Planner:

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
            event_callback
            or (lambda message: None)
        )

    def create_plan(
        self,
        user_text: str,
        context: str,
        user_name: str = "",
        language: str = "de"
    ):

        self.event_callback(
            "Brain: analyzing objective"
        )

        tools = self.registry.schemas()

        tool_summary = []

        for tool in tools:

            function = tool.get(
                "function",
                {}
            )

            tool_summary.append({
                "name":
                    function.get("name"),

                "description":
                    function.get("description")
            })

        prompt = f"""
You are DMC's central planning engine.

Your job is to understand the user's actual goal
and determine how DMC can accomplish it.

You are NOT limited to specialized tools.

IMPORTANT PRINCIPLE:

The absence of a specialized tool does NOT mean
that a capability is missing.

DMC may use general-purpose capabilities such as:

- shell
- Python
- filesystem
- process inspection
- network inspection
- web research

to accomplish tasks.

You must try to solve problems with existing
general-purpose capabilities before declaring
a capability missing.


========================================
REQUEST CLASSIFICATION
========================================

Classify the request as one of:

1. conversation
2. computer_task
3. research
4. capability_required


========================================
CONVERSATION
========================================

Use "conversation" for normal conversation,
questions, explanations, greetings and questions
about DMC itself.

Examples:

"Hallo"

"Wer bist du?"

"Was kannst du?"

"Was ist Python?"

These do not require tools.


========================================
COMPUTER TASK
========================================

Use "computer_task" when the user wants DMC
to actually perform or inspect something
on the computer.

Examples:

"Analysiere meinen Computer."

"Erstelle eine Datei."

"Starte einen Server."

"Öffne Python."

"Zeig mir meine IP-Adresse."


========================================
RESEARCH
========================================

Use "research" when the user explicitly asks
for Internet research.

Examples:

"Recherchiere, wie Samba funktioniert."

"Suche auf GitHub nach einer Lösung."


========================================
CAPABILITY REQUIRED
========================================

Use "capability_required" ONLY when:

1. the user's request genuinely requires an action,
2. the existing tools cannot reasonably perform it,
3. general-purpose tools cannot reasonably perform it,
4. and no reasonable research-based approach is available.

Do NOT use capability_required simply because
a specialized tool does not exist.


========================================
GENERAL-PURPOSE TOOLS
========================================

If a specialized capability is missing,
consider whether one of these can solve it:

- shell commands
- Python scripts
- filesystem operations
- process inspection
- network inspection
- existing system tools
- web research


For example:

If there is no GPU information tool but
a shell tool exists, DMC may investigate:

- nvidia-smi
- wmic
- PowerShell
- system utilities
- Python libraries

before declaring GPU information unavailable.


========================================
USER REQUEST
========================================

USER:
{user_text}

USER NAME:
{user_name or "not provided"}

LANGUAGE:
{language}

MEMORY:
{context}


========================================
AVAILABLE TOOLS
========================================

{json.dumps(tool_summary, indent=2)}


========================================
PLANNING RULES
========================================

1. Understand the actual objective.

2. Break complicated tasks into smaller steps.

3. Use existing specialized tools when appropriate.

4. If a specialized tool does not exist,
   consider general-purpose tools.

5. Shell and Python can be used to investigate
   and solve many problems.

6. Web research can be used when current information
   or documentation is required.

7. Do not declare a capability missing merely
   because a specialized tool does not exist.

8. Capability gaps should be rare.

9. Every important action should have a verification
   method.

10. Never invent tool names.

11. Never claim that an action succeeded without evidence.


========================================
OUTPUT
========================================

Return ONLY valid JSON.

Use exactly:

{{
    "category":
        "conversation | computer_task | research | capability_required",

    "goal":
        "short description of the actual goal",

    "complexity":
        "simple | multi_step | unknown",

    "requires_tools":
        true,

    "steps": [
        {{
            "objective":
                "what this step accomplishes",

            "preferred_tools":
                ["tool_name"],

            "verification":
                "how to verify this step",

            "fallback_strategy":
                "what to try if the preferred tool cannot provide the information"
        }}
    ],

    "capability_gap":
        false,

    "missing_capability":
        "",

    "success_criteria": []
}}
"""

        response = self.llm.chat([
            {
                "role":
                    "system",

                "content":
                    (
                        "You are DMC's central "
                        "planning engine. "
                        "Return valid JSON only."
                    )
            },
            {
                "role":
                    "user",

                "content":
                    prompt
            }
        ])

        content = (
            response.get(
                "content"
            )
            or ""
        ).strip()

        plan = self._parse_json(
            content
        )

        if not plan:

            self.event_callback(
                "Brain: invalid planner output"
            )

            return {
                "category":
                    "conversation",

                "goal":
                    user_text,

                "complexity":
                    "simple",

                "requires_tools":
                    False,

                "steps":
                    [],

                "capability_gap":
                    False,

                "missing_capability":
                    "",

                "success_criteria":
                    []
            }

        category = plan.get(
            "category"
        )

        # Conversation must NEVER
        # trigger a capability gap.

        if category == "conversation":

            plan["requires_tools"] = False

            plan["capability_gap"] = False

            plan["steps"] = []

        return plan

    @staticmethod
    def _parse_json(content):

        try:

            return json.loads(
                content
            )

        except json.JSONDecodeError:

            pass

        if "```" in content:

            for part in content.split(
                "```"
            ):

                cleaned = part.strip()

                if cleaned.startswith(
                    "json"
                ):

                    cleaned = (
                        cleaned[4:]
                        .strip()
                    )

                try:

                    return json.loads(
                        cleaned
                    )

                except json.JSONDecodeError:

                    continue

        return None
