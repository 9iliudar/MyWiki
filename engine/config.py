import os
from pathlib import Path

import yaml


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for section in ("llm", "embedding"):
        env_var = config[section].get("api_key_env")
        if env_var:
            config[section]["api_key"] = os.environ.get(env_var, "")

    return config
