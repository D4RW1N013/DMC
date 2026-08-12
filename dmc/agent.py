from .brain import Brain
from .fast_path import FastPath


class Agent:

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
            event_callback or
            (lambda message: None)
        )

        self.confirm_callback = (
            confirm_callback or
            (lambda tool, args: True)
        )

        self.brain = Brain(
            llm=llm,
            registry=registry,
            memory=memory,
            settings=settings,
            event_callback=self.event_callback,
            confirm_callback=self.confirm_callback
        )

        self.fast_path = FastPath(
            llm=llm,
            registry=registry,
            settings=settings,
            event_callback=self.event_callback,
            confirm_callback=self.confirm_callback
        )

    def run(
        self,
        user_text,
        user_name="",
        language="de"
    ):

        # Cheap classification based on the request.
        # Complex requests are sent to the full Brain.

        complex_markers = [
            "recherchiere",
            "recherchier",
            "suche im internet",
            "im internet",
            "finde heraus",
            "entwickle",
            "programmiere",
            "baue",
            "erstelle ein projekt",
            "repariere",
            "debugge",
            "analysiere vollständig",
            "selbstständig",
            "selbständig",
            "github",
            "samba",
            "server einrichten",
            "mehrere schritte",
            "wenn etwas nicht funktioniert",
            "teste anschließend",
            "überprüfe anschließend"
        ]

        text = user_text.lower().strip()

        is_complex = any(
            marker in text
            for marker in complex_markers
        )

        if is_complex:

            self.event_callback(
                "Router: complex request → Brain"
            )

            return self.brain.run(
                user_text=user_text,
                user_name=user_name,
                language=language
            )

        self.event_callback(
            "Router: simple request → FastPath"
        )

        return self.fast_path.run(
            user_text=user_text,
            user_name=user_name,
            language=language
        )
