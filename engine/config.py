import os
from pathlib import Path

import yaml


def _load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def load_config(config_path: str = None) -> dict:
    _load_dotenv()

    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for section in ("llm", "embedding"):
        env_var = config[section].get("api_key_env")
        if env_var:
            config[section]["api_key"] = os.environ.get(env_var, "")

    return config
