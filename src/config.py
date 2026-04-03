# Configuration and state management for playte photo frame

import json

CONFIG_PATH = "/sd/config.json"
STATE_PATH = "/sd/state.json"

DEFAULT_CONFIG = {
    "interval_minutes": 60,
    "order": "sequential"
}


def load_config():
    """Load config.json from SD card, returning defaults if missing or invalid."""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        # Merge with defaults for any missing keys
        result = DEFAULT_CONFIG.copy()
        result.update(config)
        return result
    except (OSError, ValueError):
        return DEFAULT_CONFIG.copy()


def load_state():
    """Load state.json from SD card, returning None if missing."""
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_state(state):
    """Save state.json to SD card."""
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)
