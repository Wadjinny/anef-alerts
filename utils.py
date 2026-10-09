"""Petits utilitaires de formatage partagés."""

from datetime import datetime
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")


def format_dt_fr(dt_or_iso, include_seconds: bool = False) -> str:
    """Formate une date (ISO string ou datetime) en français, fuseau Europe/Paris.
    Ex: "9 octobre 2026 à 15:32"."""
    if not dt_or_iso:
        return "—"
    if isinstance(dt_or_iso, str):
        try:
            dt = datetime.fromisoformat(dt_or_iso)
        except ValueError:
            return dt_or_iso
    else:
        dt = dt_or_iso

    if dt.tzinfo is None:
        dt = dt.astimezone()  # suppose heure locale de la machine
    dt = dt.astimezone(PARIS)

    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"][dt.month - 1]
    heure = dt.strftime("%H:%M:%S" if include_seconds else "%H:%M")
    return f"{dt.day} {mois} {dt.year} à {heure}"
