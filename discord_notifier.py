"""Envoi de notifications vers un webhook Discord."""

import httpx

from utils import format_dt_fr


def send_webhook(webhook_url: str, content: str = None, embed: dict = None):
    payload = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]
    resp = httpx.post(webhook_url, json=payload, timeout=15.0)
    resp.raise_for_status()


def send_status_change(webhook_url: str, status_info: dict, previous_info: dict | None, date_statut, checked_at):
    """status_info / previous_info : dicts renvoyés par get_status_explanation() (previous_info peut être None)."""
    color = {
        1: 0x6b7280, 2: 0x6b7280,
        3: 0x3b82f6, 4: 0x3b82f6, 5: 0x3b82f6,
        6: 0x8b5cf6, 7: 0x8b5cf6, 8: 0x8b5cf6,
        9: 0xf59e0b, 10: 0xf59e0b, 11: 0xf59e0b,
        12: 0x10b981,
    }.get(status_info["etape"], 0x6b7280)

    fields = [{"name": "Étape", "value": f"{status_info['etape']}/12", "inline": True}]

    if previous_info:
        fields.append({
            "name": "Statut précédent",
            "value": f"{previous_info['icon']} {previous_info['phase']} — {previous_info['explication']}",
            "inline": False,
        })

    fields.append({"name": "Statut depuis le", "value": format_dt_fr(date_statut), "inline": True})

    embed = {
        "title": f"{status_info['icon']} {status_info['phase']}",
        "description": status_info["explication"],
        "color": color,
        "fields": fields,
        "footer": {"text": f"ANEF Status Tracker (bot) — vérifié le {format_dt_fr(checked_at, include_seconds=True)}"},
    }

    send_webhook(webhook_url, embed=embed)


def send_error(webhook_url: str, message: str):
    send_webhook(webhook_url, content=f"⚠️ **ANEF Status Tracker** — {message}")


def send_recovery(webhook_url: str, message: str = "les vérifications fonctionnent à nouveau."):
    send_webhook(webhook_url, content=f"✅ **ANEF Status Tracker** — Rétabli : {message}")
