from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ..models import Tool


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_command(
    command: list[str],
    cwd: Path | None = None,
    timeout: int = 120,
):
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except FileNotFoundError as exc:
        return 127, "", str(exc)

    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out."


# ============================================================
# GitHub authentication
# ============================================================

def github_status() -> str:

    code, stdout, stderr = run_command(
        [
            "gh",
            "auth",
            "status",
            "--hostname",
            "github.com",
        ],
        timeout=30,
    )

    if code != 0:
        return (
            "GITHUB_NOT_AUTHENTICATED\n"
            "GitHub CLI is not authenticated."
        )

    return (
        "GITHUB_AUTHENTICATED\n\n"
        + (stdout or stderr)
    )


def github_login() -> str:

    code, stdout, stderr = run_command(
        [
            "gh",
            "auth",
            "login",
            "--hostname",
            "github.com",
            "--web",
            "--git-protocol",
            "https",
        ],
        timeout=300,
    )

    if code != 0:
        return (
            "ERROR: GitHub login failed.\n"
            + (stderr or stdout)
        )

    return (
        "GitHub login completed.\n"
        + (stdout or "")
    )


# ============================================================
# Project analysis
# ============================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
}


SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "secrets.json",
    "credentials.json",
    "token.json",
}


SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


def is_ignored(
    path: Path,
    root: Path,
) -> bool:

    relative = path.relative_to(root)

    return any(
        part.lower() in IGNORED_DIRECTORIES
        for part in relative.parts
    )


def is_sensitive(path: Path) -> bool:

    filename = path.name.lower()

    if filename in {
        name.lower()
        for name in SENSITIVE_FILENAMES
    }:
        return True

    return path.suffix.lower() in SENSITIVE_EXTENSIONS


def scan_project() -> dict:

    root = project_root()

    publish = []
    excluded = []
    sensitive = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        relative = path.relative_to(root)
        relative_string = str(relative)

        if is_ignored(path, root):

            excluded.append(
                relative_string
            )

            continue

        if is_sensitive(path):

            sensitive.append(
                relative_string
            )

            continue

        publish.append(
            relative_string
        )

    return {
        "project": "DMC",
        "root": str(root),
        "publish": sorted(publish),
        "excluded": sorted(excluded),
        "sensitive": sorted(sensitive),
    }


def github_analyze_project() -> str:

    return json.dumps(
        scan_project(),
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# Prepare publication plan
# ============================================================

def github_prepare_publish(
    repository_name: str = "DMC",
    visibility: str = "private",
) -> str:

    visibility = visibility.lower().strip()

    if visibility not in {
        "private",
        "public",
    }:

        return (
            "ERROR: visibility must be "
            "private or public."
        )

    scan = scan_project()

    plan = {
        "action": "publish_project",
        "project": scan["project"],
        "root": scan["root"],
        "repository_name": repository_name,
        "visibility": visibility,
        "files_to_publish": scan["publish"],
        "files_excluded": scan["excluded"],
        "sensitive_files_blocked": scan["sensitive"],
        "files_to_create": [
            "README.md",
            ".gitignore",
            "install_dmc_windows.bat",
            "install_dmc_macos.sh",
        ],
        "upload_allowed": len(
            scan["sensitive"]
        ) == 0,
    }

    return json.dumps(
        plan,
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# Release files
# ============================================================

def create_release_files(
    root: Path,
    repository_name: str,
) -> None:

    readme = root / "README.md"

    readme_content = (
        f"# {repository_name}\n\n"
        "## DMC — Digital Machine Companion\n\n"
        "DMC is a local AI computer agent.\n\n"
        "## Requirements\n\n"
        "- Python 3.11+\n"
        "- Ollama\n"
        "- Qwen3 8B\n\n"
        "## Start\n\n"
        "```bash\n"
        "python -m dmc\n"
        "```\n\n"
        "## Features\n\n"
        "- Local LLM\n"
        "- Computer tools\n"
        "- File system tools\n"
        "- Network tools\n"
        "- Web tools\n"
        "- Persistent memory\n"
        "- GitHub integration\n\n"
        "## Security\n\n"
        "Potentially dangerous actions require confirmation.\n"
    )

    readme.write_text(
        readme_content,
        encoding="utf-8",
    )

    gitignore = root / ".gitignore"

    additions = """
# Python
__pycache__/
*.py[cod]

# Virtual environments
.venv/
venv/
env/

# IDE
.idea/
.vscode/

# Secrets
.env
.env.*
!.env.example

# Local DMC memory
data/memory.json

# Logs
*.log
"""

    existing = ""

    if gitignore.exists():

        existing = gitignore.read_text(
            encoding="utf-8",
            errors="replace",
        )

    if additions.strip() not in existing:

        gitignore.write_text(
            existing.rstrip()
            + "\n"
            + additions,
            encoding="utf-8",
        )

    windows_installer = (
        root / "install_dmc_windows.bat"
    )

    windows_installer.write_text(
        r"""@echo off
setlocal

title DMC Installer

echo ==========================================
echo DMC - Digital Machine Companion
echo ==========================================
echo.

where python >nul 2>&1

if errorlevel 1 (
    echo Python was not found.
    echo Please install Python 3.11 or newer.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

where ollama >nul 2>&1

if errorlevel 1 (
    echo Ollama was not found.
    echo Please install Ollama.
    start https://ollama.com/download
    pause
    exit /b 1
)

python -m pip install -r requirements.txt

ollama pull qwen3:8b

python -m dmc

pause
""",
        encoding="utf-8",
    )

    mac_installer = (
        root / "install_dmc_macos.sh"
    )

    mac_installer.write_text(
        """#!/bin/bash

set -e

echo "DMC Installer"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required."
    exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama is required."
    exit 1
fi

python3 -m pip install -r requirements.txt

ollama pull qwen3:8b

python3 -m dmc
""",
        encoding="utf-8",
    )


# ============================================================
# Publish project
# ============================================================

def github_publish_project(
    repository_name: str = "DMC",
    description: str = (
        "DMC - Digital Machine Companion"
    ),
    visibility: str = "private",
) -> str:

    root = project_root()

    visibility = visibility.lower().strip()

    if visibility not in {
        "private",
        "public",
    }:

        return (
            "ERROR: visibility must be "
            "private or public."
        )

    # Check GitHub authentication.

    code, stdout, stderr = run_command(
        [
            "gh",
            "auth",
            "status",
            "--hostname",
            "github.com",
        ],
        timeout=30,
    )

    if code != 0:

        return (
            "ERROR: GitHub authentication required.\n"
            + (stderr or stdout)
        )

    # Scan again immediately before publishing.

    scan = scan_project()

    if scan["sensitive"]:

        return (
            "SECURITY_BLOCK\n\n"
            "The following sensitive files "
            "must not be published:\n\n"
            + "\n".join(
                "- " + item
                for item in scan["sensitive"]
            )
        )

    # Create release files.

    create_release_files(
        root,
        repository_name,
    )

    # Initialize Git if necessary.

    if not (root / ".git").exists():

        code, stdout, stderr = run_command(
            ["git", "init"],
            cwd=root,
            timeout=30,
        )

        if code != 0:

            return (
                "ERROR: git init failed.\n"
                + (stderr or stdout)
            )

    # Stage files.

    code, stdout, stderr = run_command(
        ["git", "add", "."],
        cwd=root,
        timeout=60,
    )

    if code != 0:

        return (
            "ERROR: git add failed.\n"
            + (stderr or stdout)
        )

    # Commit.

    code, stdout, stderr = run_command(
        [
            "git",
            "commit",
            "-m",
            "DMC release",
        ],
        cwd=root,
        timeout=60,
    )

    if code != 0:

        combined = (
            stdout
            + "\n"
            + stderr
        ).lower()

        if (
            "nothing to commit"
            not in combined
            and "nothing added to commit"
            not in combined
        ):

            return (
                "ERROR: git commit failed.\n"
                + (stderr or stdout)
            )

    # Create GitHub repository and push.

    visibility_flag = (
        "--public"
        if visibility == "public"
        else "--private"
    )

    code, stdout, stderr = run_command(
        [
            "gh",
            "repo",
            "create",
            repository_name,
            visibility_flag,
            "--description",
            description,
            "--source",
            str(root),
            "--remote",
            "origin",
            "--push",
        ],
        cwd=root,
        timeout=180,
    )

    if code != 0:

        return (
            "ERROR: GitHub repository creation failed.\n"
            + (stderr or stdout)
        )

    # Verify remote.

    code, remote, stderr = run_command(
        [
            "git",
            "remote",
            "get-url",
            "origin",
        ],
        cwd=root,
        timeout=30,
    )

    if code != 0:

        remote = "Unknown"

    return (
        "GITHUB_PUBLISH_SUCCESS\n\n"
        f"Repository: {repository_name}\n"
        f"Visibility: {visibility}\n"
        f"Remote: {remote}\n\n"
        "DMC successfully published the project."
    )


# ============================================================
# Tool registration
# ============================================================

def register(registry):

    registry.register(
        Tool(
            name="github_status",
            description=(
                "Check whether GitHub CLI authentication "
                "is active."
            ),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=github_status,
            risk="SAFE",
        )
    )

    registry.register(
        Tool(
            name="github_login",
            description=(
                "Open the GitHub browser login flow."
            ),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=github_login,
            risk="CONFIRM",
        )
    )

    registry.register(
        Tool(
            name="github_analyze_project",
            description=(
                "Analyze the DMC project and identify "
                "files that can be published, files that "
                "should be excluded, and potentially "
                "sensitive files."
            ),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=github_analyze_project,
            risk="SAFE",
        )
    )

    registry.register(
        Tool(
            name="github_prepare_publish",
            description=(
                "Create a detailed publication plan for "
                "the DMC project. Determine which files "
                "belong to the project, which local files "
                "must be excluded, which sensitive files "
                "must be blocked, and which release files "
                "should be generated. Do not upload anything."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "repository_name": {
                        "type": "string",
                        "description": (
                            "Name of the GitHub repository."
                        ),
                    },
                    "visibility": {
                        "type": "string",
                        "enum": [
                            "private",
                            "public",
                        ],
                        "description": (
                            "GitHub repository visibility."
                        ),
                    },
                },
                "required": [
                    "repository_name",
                    "visibility",
                ],
                "additionalProperties": False,
            },
            handler=github_prepare_publish,
            risk="SAFE",
        )
    )

    registry.register(
        Tool(
            name="github_publish_project",
            description=(
                "Publish the prepared DMC project to GitHub. "
                "This creates release files, initializes Git, "
                "commits the project, creates the GitHub "
                "repository and pushes the project."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "repository_name": {
                        "type": "string",
                        "description": (
                            "Name of the GitHub repository."
                        ),
                    },
                    "description": {
                        "type": "string",
                        "description": (
                            "Short repository description."
                        ),
                    },
                    "visibility": {
                        "type": "string",
                        "enum": [
                            "private",
                            "public",
                        ],
                        "description": (
                            "Repository visibility."
                        ),
                    },
                },
                "required": [
                    "repository_name",
                    "description",
                    "visibility",
                ],
                "additionalProperties": False,
            },
            handler=github_publish_project,
            risk="DANGEROUS",
        )
    )