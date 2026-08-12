from flask import Flask, jsonify, render_template, request
import threading
import uuid

from .config import settings
from .llm import LLM
from .memory import Memory
from .tool_registry import ToolRegistry
from .tools import register_all
from .agent import Agent


class DMCWebApp:

    def __init__(self):

        self.registry = ToolRegistry()

        register_all(
            self.registry
        )

        self.memory = Memory(
            settings.memory_file
        )

        self.llm = LLM(
            settings
        )

        self.jobs = {}

        self.flask = Flask(
            __name__,
            template_folder="web/templates",
            static_folder="web/static"
        )

        self.setup_routes()


    def setup_routes(self):

        # =====================================================
        # MAIN PAGE
        # =====================================================

        @self.flask.route("/")
        def index():

            return render_template(
                "index.html",
                model=settings.ollama_model
            )


        # =====================================================
        # START CHAT JOB
        # =====================================================

        @self.flask.route(
            "/api/chat",
            methods=["POST"]
        )
        def chat():

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            message = str(
                data.get(
                    "message",
                    ""
                )
            ).strip()

            user_name = str(
                data.get(
                    "user_name",
                    ""
                )
            ).strip()

            language = str(
                data.get(
                    "language",
                    "de"
                )
            ).strip()

            if not message:

                return jsonify({
                    "error": "Empty message."
                }), 400

            job_id = uuid.uuid4().hex

            self.jobs[job_id] = {
                "status": "running",
                "message": message,
                "answer": None,
                "events": [],
                "confirmation": None,
                "error": None
            }

            thread = threading.Thread(
                target=self.run_agent,
                args=(
                    job_id,
                    message,
                    user_name,
                    language
                ),
                daemon=True
            )

            thread.start()

            return jsonify({
                "job_id": job_id
            })


        # =====================================================
        # JOB STATUS
        # =====================================================

        @self.flask.route(
            "/api/jobs/<job_id>"
        )
        def job_status(job_id):

            job = self.jobs.get(
                job_id
            )

            if not job:

                return jsonify({
                    "error": "Unknown job."
                }), 404

            confirmation = job.get(
                "confirmation"
            )

            # IMPORTANT:
            # threading.Event is an internal Python object
            # and cannot be serialized to JSON.
            #
            # Only expose the information that the frontend
            # actually needs.

            safe_confirmation = None

            if confirmation:

                safe_confirmation = {
                    "tool": confirmation.get(
                        "tool"
                    ),
                    "risk": confirmation.get(
                        "risk"
                    ),
                    "args": confirmation.get(
                        "args"
                    )
                }

            return jsonify({
                "status": job["status"],
                "answer": job["answer"],
                "events": job["events"][-50:],
                "confirmation": safe_confirmation,
                "error": job["error"]
            })


        # =====================================================
        # CONFIRMATION
        # =====================================================

        @self.flask.route(
            "/api/jobs/<job_id>/confirm",
            methods=["POST"]
        )
        def confirm(job_id):

            job = self.jobs.get(
                job_id
            )

            if not job:

                return jsonify({
                    "error": "Unknown job."
                }), 404

            confirmation = job.get(
                "confirmation"
            )

            if not confirmation:

                return jsonify({
                    "error":
                        "No confirmation pending."
                }), 400

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            allowed = bool(
                data.get(
                    "allowed",
                    False
                )
            )

            # Store the user's decision.
            confirmation["answer"] = allowed

            # Wake up the waiting agent thread.
            event = confirmation.get(
                "event"
            )

            if event:
                event.set()

            return jsonify({
                "ok": True
            })


        # =====================================================
        # SERVER STATUS
        # =====================================================

        @self.flask.route(
            "/api/status"
        )
        def status():

            return jsonify({
                "status": "online",
                "model":
                    settings.ollama_model,
                "provider":
                    settings.llm_provider
            })


    # =========================================================
    # RUN AGENT
    # =========================================================

    def run_agent(
        self,
        job_id,
        message,
        user_name,
        language
    ):

        def event_callback(event):

            job = self.jobs.get(
                job_id
            )

            if not job:
                return

            job["events"].append(
                str(event)
            )


        def confirm_callback(
            tool,
            args
        ):

            event = threading.Event()

            self.jobs[
                job_id
            ]["confirmation"] = {
                "tool": tool.name,
                "risk": tool.risk,
                "args": args,

                # Internal synchronization object.
                # NEVER send this object through jsonify().
                "event": event,

                "answer": False
            }

            self.jobs[
                job_id
            ]["status"] = (
                "waiting_confirmation"
            )

            # Wait until the web interface answers.
            event.wait()

            confirmation = (
                self.jobs[
                    job_id
                ].get(
                    "confirmation"
                )
            )

            allowed = bool(
                confirmation
                and confirmation.get(
                    "answer"
                )
            )

            self.jobs[
                job_id
            ]["confirmation"] = None

            self.jobs[
                job_id
            ]["status"] = "running"

            return allowed


        try:

            agent = Agent(
                self.llm,
                self.registry,
                self.memory,
                settings,
                event_callback=event_callback,
                confirm_callback=confirm_callback
            )

            answer = agent.run(
                message,
                user_name=user_name,
                language=language
            )

            self.jobs[
                job_id
            ]["answer"] = answer

            self.jobs[
                job_id
            ]["status"] = "completed"


        except Exception as exc:

            self.jobs[
                job_id
            ]["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

            self.jobs[
                job_id
            ]["status"] = "error"


    # =========================================================
    # START WEB SERVER
    # =========================================================

    def run(
        self,
        host="127.0.0.1",
        port=5000
    ):

        print()
        print(
            "===================================="
        )
        print(
            " DMC — Digital Machine Companion"
        )
        print(
            "===================================="
        )
        print()

        print(
            f"Web interface: "
            f"http://{host}:{port}"
        )

        print()

        self.flask.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )


# =============================================================
# WEB ENTRY POINT
# =============================================================

def run_web():

    app = DMCWebApp()

    app.run(
        host="127.0.0.1",
        port=5000
    )