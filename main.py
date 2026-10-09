"""
Vérifie périodiquement le statut du dossier de naturalisation ANEF et notifie
tout changement sur un webhook Discord.

Configuration via .env (voir .env.example) :
  ANEF_LOGIN               numéro de visa/titre de séjour utilisé pour se connecter
  ANEF_PASSWORD            mot de passe du compte ANEF
  DISCORD_WEBHOOK_URL      URL du webhook Discord
  CHECK_INTERVAL_MINUTES   intervalle entre deux vérifications (def. 30)
"""

import argparse
import os
import sys
import time
import traceback
from datetime import datetime

# La console Windows par défaut (cp1252) ne sait pas afficher les emoji des
# libellés de statut (status_data.py) : on force stdout/stderr en UTF-8.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from anef_client import AnefClient, AnefAuthError
from anef_mapper import derive_status
from status_data import get_status_explanation
from state import load_state, save_state, reset_state, STATE_FILE
from discord_notifier import send_status_change, send_error, send_webhook
from utils import format_dt_fr

load_dotenv()

ANEF_LOGIN = os.environ.get("ANEF_LOGIN")
ANEF_PASSWORD = os.environ.get("ANEF_PASSWORD")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL_MINUTES = float(os.environ.get("CHECK_INTERVAL_MINUTES", "30"))


def log(message: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def check_once():
    state = load_state()
    previous_code = state.get("statutCode")
    previous_date = state.get("dateStatut")
    previous_info = get_status_explanation(previous_code) if previous_code else None

    with AnefClient(ANEF_LOGIN, ANEF_PASSWORD) as client:
        client.login()
        snapshot = client.fetch_dossier_snapshot()

    now = datetime.now().isoformat()

    if snapshot is None:
        log("Aucun dossier exploitable renvoyé par l'API.")
        save_state({**state, "lastCheckedAt": now})
        return

    derived = derive_status(
        statut=snapshot["statut_raw"],
        frise=snapshot["frise"],
        notifications=snapshot["notifications"],
        dossier_id=snapshot["id"],
        numero_decret=snapshot["numero_decret"],
    )
    statut_code = derived["statutCode"]
    date_statut = snapshot["date_statut"]

    if not statut_code:
        log("Statut non exploitable (ni frise, ni macro, ni notification connue).")
        save_state({**state, "lastCheckedAt": now})
        return

    changed = statut_code != previous_code or date_statut != previous_date
    status_info = get_status_explanation(statut_code)

    if changed:
        log(f"Changement détecté : {previous_code or '(aucun)'} -> {statut_code} ({status_info['explication']})")
        send_status_change(DISCORD_WEBHOOK_URL, status_info, previous_info, date_statut, now)
        save_state({
            "statutCode": statut_code,
            "dateStatut": date_statut,
            "lastChangedAt": now,
            "lastCheckedAt": now,
        })
    else:
        log(f"Pas de changement (toujours : {statut_code} — {status_info['explication']}, vérifié le {format_dt_fr(now, include_seconds=True)})")
        save_state({**state, "lastCheckedAt": now})


def require_env(*names):
    missing = [n for n in names if not globals()[n]]
    if missing:
        print(f"Variables manquantes dans .env : {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def cmd_reset():
    existed = reset_state()
    log(f"État réinitialisé ({STATE_FILE} supprimé)." if existed else "Rien à réinitialiser (pas d'état enregistré).")


def cmd_test_webhook():
    require_env("DISCORD_WEBHOOK_URL")
    log("Envoi d'un message de test au webhook Discord...")
    send_webhook(DISCORD_WEBHOOK_URL, content="✅ **anef-notifier** — test du webhook, tout fonctionne.")
    log("Message envoyé. Vérifiez le salon Discord.")


def cmd_test_login():
    require_env("ANEF_LOGIN", "ANEF_PASSWORD")
    log("Tentative de connexion ANEF...")
    try:
        with AnefClient(ANEF_LOGIN, ANEF_PASSWORD) as client:
            client.login()
            log("✅ Connexion réussie.")
            snapshot = client.fetch_dossier_snapshot()
    except AnefAuthError as e:
        log(f"❌ Échec de connexion : {e}")
        sys.exit(1)

    if snapshot is None:
        log("Connecté, mais aucun dossier exploitable n'a été renvoyé par l'API.")
        return

    derived = derive_status(
        statut=snapshot["statut_raw"],
        frise=snapshot["frise"],
        notifications=snapshot["notifications"],
        dossier_id=snapshot["id"],
        numero_decret=snapshot["numero_decret"],
    )
    if not derived["statutCode"]:
        log("Connecté, mais statut non exploitable (ni frise, ni macro, ni notification connue).")
        return

    status_info = get_status_explanation(derived["statutCode"])
    log(f"Statut actuel : {status_info['icon']} {status_info['phase']} — {status_info['explication']} (étape {status_info['etape']}/12)")
    log(f"Statut depuis le : {format_dt_fr(snapshot['date_statut'])}")


def cmd_status():
    state = load_state()
    if not state.get("statutCode"):
        log("Aucun état enregistré pour l'instant (lancez --once ou --test-login).")
        return

    status_info = get_status_explanation(state["statutCode"])
    log(f"Statut connu : {status_info['icon']} {status_info['phase']} — {status_info['explication']} (étape {status_info['etape']}/12)")
    log(f"Statut depuis le : {format_dt_fr(state.get('dateStatut'))}")
    log(f"Dernier changement détecté le : {format_dt_fr(state.get('lastChangedAt'), include_seconds=True)}")
    log(f"Dernière vérification le : {format_dt_fr(state.get('lastCheckedAt'), include_seconds=True)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Vérifie et notifie les changements de statut ANEF.")
    parser.add_argument("--once", action="store_true", help="Fait une seule vérification puis quitte (au lieu de boucler).")
    parser.add_argument("--reset", action="store_true", help="Réinitialise l'état local (state.json) puis quitte.")
    parser.add_argument("--test-webhook", action="store_true", help="Envoie un message de test au webhook Discord puis quitte.")
    parser.add_argument("--test-login", action="store_true", help="Teste uniquement la connexion ANEF (et affiche le statut courant) puis quitte.")
    parser.add_argument("--status", action="store_true", help="Affiche le dernier état enregistré (sans appeler l'API ANEF) puis quitte.")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.reset:
        cmd_reset()
        return
    if args.test_webhook:
        cmd_test_webhook()
        return
    if args.test_login:
        cmd_test_login()
        return
    if args.status:
        cmd_status()
        return

    require_env("ANEF_LOGIN", "ANEF_PASSWORD", "DISCORD_WEBHOOK_URL")

    log(f"Démarrage. Intervalle : {CHECK_INTERVAL_MINUTES} min." if not args.once else "Démarrage (mode --once).")

    while True:
        try:
            check_once()
        except AnefAuthError as e:
            log(f"Échec de connexion ANEF : {e}")
            try:
                send_error(DISCORD_WEBHOOK_URL, f"Échec de connexion ANEF : {e}")
            except Exception:
                pass
        except Exception:
            log("Erreur inattendue :\n" + traceback.format_exc())
            try:
                send_error(DISCORD_WEBHOOK_URL, "Erreur inattendue, voir les logs du script.")
            except Exception:
                pass

        if args.once:
            break
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
