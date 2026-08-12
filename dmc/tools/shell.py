import os
import platform
import subprocess
import uuid
from pathlib import Path

from ..models import Tool


_PROCESSES = {}


# Befehle, die typischerweise dauerhaft laufen.
# Diese dürfen nicht über run_shell gestartet werden.
LONG_RUNNING_PATTERNS = [
    "python -m http.server",
    "python -m flask",
    "flask run",
    "uvicorn",
    "gunicorn",
    "node server",
    "npm start",
    "npm run dev",
    "minecraft",
    "java -jar",
    "mysqld",
    "postgres",
    "redis-server",
]


def _command(command):
    if platform.system() == "Windows":
        return [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ]

    return [
        "/bin/bash",
        "-lc",
        command,
    ]


def _decode(data):
    if data is None or isinstance(data, str):
        return data or ""

    for encoding in ("utf-8", "cp1252", "cp850"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass

    return data.decode("utf-8", errors="replace")


def _looks_like_long_running(command):
    command_lower = command.lower()

    return any(
        pattern in command_lower
        for pattern in LONG_RUNNING_PATTERNS
    )


def register(registry):

    # =========================================================
    # NORMALE SHELL-BEFEHLE
    # =========================================================

    def run_shell(command, cwd=None, timeout=120):

        # Verhindert, dass DMC versehentlich einen Server
        # über das normale Shell-Tool startet.
        if _looks_like_long_running(command):

            return (
                "ERROR: This command appears to start a long-running "
                "process or server.\n"
                "Do NOT use run_shell for this command.\n"
                "Use start_process instead."
            )

        try:

            process = subprocess.Popen(
                _command(command),
                cwd=str(Path(cwd).expanduser())
                if cwd
                else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
            )

            try:

                stdout, stderr = process.communicate(
                    timeout=timeout
                )

            except subprocess.TimeoutExpired:

                # -------------------------------------------------
                # WINDOWS
                # -------------------------------------------------

                if platform.system() == "Windows":

                    try:
                        subprocess.run(
                            [
                                "taskkill",
                                "/PID",
                                str(process.pid),
                                "/T",
                                "/F",
                            ],
                            capture_output=True,
                            timeout=10,
                        )
                    except Exception:
                        try:
                            process.kill()
                        except Exception:
                            pass

                # -------------------------------------------------
                # MAC / LINUX
                # -------------------------------------------------

                else:

                    try:
                        process.kill()
                    except Exception:
                        pass

                try:
                    stdout, stderr = process.communicate(
                        timeout=10
                    )
                except subprocess.TimeoutExpired:
                    stdout = b""
                    stderr = (
                        b"Process could not be terminated cleanly."
                    )

                return (
                    f"TIMEOUT after {timeout}s\n"
                    f"EXIT CODE: {process.returncode}\n"
                    f"STDOUT:\n{_decode(stdout)}\n"
                    f"STDERR:\n{_decode(stderr)}"
                )

            return (
                f"EXIT CODE: {process.returncode}\n"
                f"STDOUT:\n{_decode(stdout)}\n"
                f"STDERR:\n{_decode(stderr)}"
            )

        except Exception as exc:

            return (
                f"ERROR starting shell command:\n"
                f"{type(exc).__name__}: {exc}"
            )

    # =========================================================
    # HINTERGRUNDPROZESS STARTEN
    # =========================================================

    def start_process(command, cwd=None, name=None):

        name = name or (
            f"dmc-{uuid.uuid4().hex[:8]}"
        )

        kwargs = {
            "cwd": (
                str(Path(cwd).expanduser())
                if cwd
                else None
            ),

            "stdout": subprocess.PIPE,

            "stderr": subprocess.STDOUT,

            "stdin": subprocess.DEVNULL,
        }

        if platform.system() == "Windows":

            kwargs["creationflags"] = (
                subprocess.CREATE_NO_WINDOW
                |
                subprocess.CREATE_NEW_PROCESS_GROUP
            )

        try:

            process = subprocess.Popen(
                _command(command),
                **kwargs,
            )

        except Exception as exc:

            return (
                f"ERROR starting background process:\n"
                f"{type(exc).__name__}: {exc}"
            )

        _PROCESSES[name] = {
            "process": process,
            "command": command,
            "cwd": cwd,
        }

        return (
            f"STARTED\n"
            f"NAME: {name}\n"
            f"PID: {process.pid}\n"
            f"COMMAND: {command}\n"
            f"CWD: {cwd or os.getcwd()}"
        )

    # =========================================================
    # PROZESSSTATUS
    # =========================================================

    def process_status(name=None):

        if name:

            item = _PROCESSES.get(name)

            if not item:
                return (
                    f"No DMC-managed process "
                    f"named {name}."
                )

            process = item["process"]

            exit_code = process.poll()

            return (
                f"NAME: {name}\n"
                f"PID: {process.pid}\n"
                f"RUNNING: {exit_code is None}\n"
                f"EXIT CODE: {exit_code}\n"
                f"COMMAND: {item['command']}\n"
                f"CWD: {item['cwd'] or os.getcwd()}"
            )

        if not _PROCESSES:
            return "No DMC-managed processes."

        results = []

        for process_name, item in _PROCESSES.items():

            process = item["process"]

            exit_code = process.poll()

            results.append(
                f"{process_name} | "
                f"PID {process.pid} | "
                f"RUNNING={exit_code is None} | "
                f"EXIT={exit_code} | "
                f"{item['command']}"
            )

        return "\n".join(results)

    # =========================================================
    # PROZESS STOPPEN
    # =========================================================

    def stop_process(name):

        item = _PROCESSES.get(name)

        if not item:

            return (
                f"No DMC-managed process "
                f"named {name}."
            )

        process = item["process"]

        if process.poll() is not None:

            return (
                f"Process {name} is already stopped "
                f"(exit code {process.returncode})."
            )

        try:

            if platform.system() == "Windows":

                subprocess.run(
                    [
                        "taskkill",
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F",
                    ],
                    capture_output=True,
                    timeout=10,
                )

            else:

                process.terminate()

        except Exception:

            try:
                process.kill()
            except Exception:
                pass

        return (
            f"STOPPED {name} "
            f"(PID {process.pid})"
        )

    # =========================================================
    # TOOLS REGISTRIEREN
    # =========================================================

    registry.register(
        Tool(
            "run_shell",

            """
            Run a short-lived shell command and wait for its result.

            IMPORTANT:
            Do not use this for HTTP servers, Flask, Uvicorn,
            Minecraft servers, databases, or other long-running
            processes. Use start_process instead.
            """,

            {
                "type": "object",

                "properties": {

                    "command": {
                        "type": "string"
                    },

                    "cwd": {
                        "type": "string"
                    },

                    "timeout": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 600
                    },
                },

                "required": [
                    "command"
                ],
            },

            run_shell,

            "CONFIRM",
        )
    )

    registry.register(
        Tool(
            "start_process",

            """
            Start a long-running process in the background.

            Use this for HTTP servers, Flask apps,
            Uvicorn, Minecraft servers, databases,
            Node servers and other services that should
            continue running after the command starts.
            """,

            {
                "type": "object",

                "properties": {

                    "command": {
                        "type": "string"
                    },

                    "cwd": {
                        "type": "string"
                    },

                    "name": {
                        "type": "string"
                    },
                },

                "required": [
                    "command"
                ],
            },

            start_process,

            "CONFIRM",
        )
    )

    registry.register(
        Tool(
            "process_status",

            """
            Check whether a DMC-managed background
            process is still running.
            """,

            {
                "type": "object",

                "properties": {

                    "name": {
                        "type": "string"
                    }

                },
            },

            process_status,
        )
    )

    registry.register(
        Tool(
            "stop_process",

            """
            Stop a DMC-managed background process.
            """,

            {
                "type": "object",

                "properties": {

                    "name": {
                        "type": "string"
                    }

                },

                "required": [
                    "name"
                ],
            },

            stop_process,

            "CONFIRM",
        )
    )