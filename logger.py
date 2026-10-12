"""
Logs persistants. Chaque appel à log() affiche sur stdout (utile en tmux) ET
ajoute au fichier anef-notifier.log, qui est tronqué aux LOG_MAX_LINES
dernières lignes pour ne jamais grossir indéfiniment sur un service qui tourne
en continu.
"""

import os
from datetime import datetime
from pathlib import Path

from utils import PARIS

LOG_FILE = Path(__file__).parent / "anef-notifier.log"
LOG_MAX_LINES = int(os.environ.get("LOG_MAX_LINES", "5000"))


def log(message: str):
    # Toujours en heure française, même si le serveur tourne en UTC (cas
    # courant sur un VPS) : évite un log à deux fuseaux différents selon la
    # ligne (voir schedule.py pour la même logique côté planification).
    timestamp = datetime.now(PARIS).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    _append_and_trim(line)


def _append_and_trim(line: str):
    try:
        existing = LOG_FILE.read_text(encoding="utf-8").splitlines() if LOG_FILE.exists() else []
        existing.extend(line.splitlines())
        if len(existing) > LOG_MAX_LINES:
            existing = existing[-LOG_MAX_LINES:]
        LOG_FILE.write_text("\n".join(existing) + "\n", encoding="utf-8")
    except OSError:
        pass  # le fichier de log ne doit jamais faire planter le script
