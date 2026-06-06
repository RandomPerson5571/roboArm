# software/config.py
import tomllib
from pathlib import Path
from typing import Any

# This ensures it works no matter where you run the script from
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE_PATH = BASE_DIR / "pyproject.toml"

def _load_config() -> dict[str, Any]:
    """Internal helper to safely load and parse the TOML file."""
    if not CONFIG_FILE_PATH.exists():
        raise FileNotFoundError(f"Configuration file missing at: {CONFIG_FILE_PATH}")
        
    with open(CONFIG_FILE_PATH, "rb") as f:
        return tomllib.load(f)

try:
    TOOL_CONFIG = _load_config().get("app", {}).get("python", {})
    print("Config loaded")
except Exception as e:
    # Fail fast on startup if the config is malformed or missing
    print(f"CRITICAL: Failed to load configuration. {e}")
    raise SystemExit(1)