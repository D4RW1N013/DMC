from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    llm_provider: str = os.getenv("DMC_LLM_PROVIDER", "ollama")
    ollama_base_url: str = os.getenv("DMC_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("DMC_OLLAMA_MODEL", "qwen3:8b")
    openai_base_url: str = os.getenv("DMC_OPENAI_BASE_URL", "")
    openai_api_key: str = os.getenv("DMC_OPENAI_API_KEY", "")
    openai_model: str = os.getenv("DMC_OPENAI_MODEL", "")
    memory_file: Path = Path(os.getenv("DMC_MEMORY_FILE", "data/memory.json"))
    workspace: Path = Path(os.getenv("DMC_WORKSPACE", "workspace"))
    max_tool_steps: int = int(os.getenv("DMC_MAX_TOOL_STEPS", "12"))
    require_confirmation: bool = os.getenv("DMC_REQUIRE_CONFIRMATION", "true").lower() == "true"

settings = Settings()
settings.memory_file.parent.mkdir(parents=True, exist_ok=True)
settings.workspace.mkdir(parents=True, exist_ok=True)
