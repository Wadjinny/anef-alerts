"""Persistance locale du dernier statut connu (évite de notifier deux fois le même statut)."""

import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / "state.json"


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_state() -> bool:
    """Supprime l'état local. Renvoie True si un fichier existait, False sinon."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        return True
    return False
