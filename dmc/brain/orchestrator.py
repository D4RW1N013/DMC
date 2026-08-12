from .planner import Planner
from .executor import Executor
from .observer import Observer
from .reflector import Reflector
from .capability_manager import CapabilityManager


class Brain:

    def __init__(
        self,
        llm,
        registry,
        memory,
        settings,
        event_callback=None,
        confirm_callback=None
    ):

        self.llm = llm
        self.registry = registry
        self.memory = memory
        self.settings = settings

        self.event_callback = (
            event_callback
            or (lambda message: None)
        )

        self.confirm_callback = (
            confirm_callback
            or (lambda tool, args: True)
        )

        self.planner = Planner(
            llm,
            registry,
            settings,
            self.event_callback
        )

        self.executor = Executor(
            llm,
            registry,
            settings,
            self.event_callback,
            self.confirm_callback
        )

        self.observer = Observer(
            llm,
            settings,
            self.event_callback
        )

        self.reflector = Reflector(
            llm,
            settings,
            self.event_callback
        )

        self.capabilities = CapabilityManager(
            llm,
            registry,
            settings,
            self.event_callback
        )

    def run(
        self,
        user_text,
        user_name="",
        language="de"
    ):

        context = self.memory.context()

        plan = self.planner.create_plan(
            user_text,
            context,
            user_name,
            language
        )

        category = plan.get(
            "category",
            "conversation"
        )

        # =====================================================
        # NORMAL CONVERSATION
        # =====================================================

        if category == "conversation":

            self.event_callback(
                "Brain: normal conversation"
            )

            return self._conversation(
                user_text,
                context,
                user_name,
                language
            )

        # =====================================================
        # CAPABILITY GAP
        # =====================================================

        if (
            category == "capability_required"
            or
            plan.get("capability_gap")
        ):

            missing = plan.get(
                "missing_capability",
                "unknown capability"
            )

            self.capabilities.inspect_gap(
                user_text,
                missing
            )

            return (
                "DMC hat erkannt, dass "
                "eine benötigte Fähigkeit fehlt: "
                f"{missing}"
            )

        # =====================================================
        # EXECUTION LOOP
        # =====================================================

        max_cycles = min(
            self.settings.max_tool_steps,
            6
        )

        current_context = context

        for cycle in range(
            max_cycles
        ):

            self.event_callback(
                f"Brain cycle "
                f"{cycle + 1}/{max_cycles}"
            )

            # ---------------------------------------------
            # EXECUTE
            # ---------------------------------------------

            results = self.executor.execute(
                user_text,
                plan,
                current_context
            )

            # ---------------------------------------------
            # OBSERVE
            # ---------------------------------------------

            observation = self.observer.verify(
                user_text,
                plan,
                results
            )

            if observation.get(
                "success"
            ):

                self.event_callback(
                    "Brain: objective verified"
                )

                return self._final_answer(
                    user_text,
                    user_name,
                    language,
                    plan,
                    results,
                    observation
                )

            # ---------------------------------------------
            # REFLECT
            # ---------------------------------------------

            reflection = self.reflector.reflect(
                user_text,
                plan,
                results,
                observation
            )

            if reflection.get(
                "capability_missing"
            ):

                missing = reflection.get(
                    "missing_capability",
                    "unknown capability"
                )

                self.capabilities.inspect_gap(
                    user_text,
                    missing
                )

                return (
                    "DMC konnte die Aufgabe "
                    "nicht abschließen, weil "
                    f"'{missing}' fehlt."
                )

            if not reflection.get(
                "retry",
                False
            ):

                return (
                    "DMC konnte die Aufgabe "
                    "nicht zuverlässig "
                    "verifizieren.\n\n"
                    "Grund: "
                    f"{reflection.get('diagnosis', '')}"
                )

            current_context += (
                "\nPrevious attempt:\n"
                f"{reflection.get('diagnosis', '')}\n"
                "Next strategy:\n"
                f"{reflection.get('next_strategy', '')}"
            )

            plan = self.planner.create_plan(
                user_text,
                current_context,
                user_name,
                language
            )

            self.event_callback(
                "Brain: replanning after failure"
            )

        return (
            "DMC hat mehrere Ansätze "
            "ausprobiert, konnte das "
            "Ergebnis aber nicht zuverlässig "
            "verifizieren."
        )

    # =========================================================
    # CONVERSATION
    # =========================================================

    def _conversation(
        self,
        user_text,
        context,
        user_name,
        language
    ):

        prompt = f"""
You are DMC, a local AI computer assistant.

The user is having a normal conversation with you.

USER:
{user_text}

USER NAME:
{user_name or "not provided"}

PREFERRED LANGUAGE:
{language}

MEMORY:
{context}

Respond naturally.

Answer in the user's selected language.

If the user asks about DMC, explain DMC based
on your actual capabilities.

Do not invent capabilities that do not exist.

Do not use tools for normal conversation unless
the user actually requests an action that requires them.
"""

        response = self.llm.chat([
            {
                "role":
                    "system",

                "content":
                    prompt
            }
        ])

        return (
            response.get(
                "content"
            )
            or
            "Hallo! Ich bin DMC."
        ).strip()

    # =========================================================
    # FINAL ANSWER
    # =========================================================

    def _final_answer(
        self,
        user_text,
        user_name,
        language,
        plan,
        results,
        observation
    ):

        prompt = f"""
You are DMC.

The user's task has been successfully verified.

USER:
{user_text}

USER NAME:
{user_name or "not provided"}

RESPONSE LANGUAGE:
{language}

PLAN:
{plan}

RESULTS:
{results}

VERIFICATION:
{observation}

Give the user a concise natural response.

Answer in the requested language.

Do not explain internal reasoning.

Do not invent results.

Only describe what was actually accomplished.
"""

        response = self.llm.chat([
            {
                "role":
                    "system",

                "content":
                    prompt
            }
        ])

        return (
            response.get(
                "content"
            )
            or
            "Task completed."
        ).strip()
