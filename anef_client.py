"""
Client HTTP pour l'API ANEF : login via le SSO Keycloak (anef-usagers) puis
récupération des signaux de statut (dossier-stepper, frise-stepper,
notifications, détail).

Flow de connexion reconstitué en observant le trafic réel du site (devtools) :
  1. GET  https://sso.anef.dgef.interieur.gouv.fr/auth/realms/anef-usagers/
          protocol/openid-connect/auth?client_id=anef-usagers&response_type=code...
       -> page de login Keycloak (HTML), contient l'URL d'action du formulaire
          (session_code/execution/tab_id).
  2. POST à cette URL d'action : {username, password, credentialId: ""}
       -> redirige (302, éventuellement en plusieurs sauts) vers
          redirect_uri#code=...&session_state=... (fragment, jamais envoyé au
          serveur : on le lit directement dans l'en-tête Location).
  3. POST /api/keycloak/token  {"code", "uri"} -> pose les cookies de session.
  4. GET /api/anf/dossier-stepper, frise-stepper, notifications, dossiers/{id}
       -> s'authentifient uniquement via ces cookies (pas de header
          Authorization nécessaire, confirmé par le trafic de l'extension).

(NB : /api/usager/login/password/keycloak, une piste explorée initialement,
n'est PAS le login standard — il exige systématiquement un champ
`new_password`, donc sert à un flux de changement de mot de passe, pas de
connexion.)
"""

import html
import re
from urllib.parse import unquote

import httpx

BASE = "https://administration-etrangers-en-france.interieur.gouv.fr"
API = f"{BASE}/api"

SSO_AUTH_URL = "https://sso.anef.dgef.interieur.gouv.fr/auth/realms/anef-usagers/protocol/openid-connect/auth"
REDIRECT_URI = f"{BASE}/usagers/#"
TOKEN_EXCHANGE_URL = f"{API}/keycloak/token"

AUTHORIZE_PARAMS = {
    "client_id": "anef-usagers",
    "theme": "portail-anef",
    "redirect_uri": REDIRECT_URI,
    "response_mode": "fragment",
    "response_type": "code",
    "scope": "openid",
    "acr_values": "eidas1",
    "ui_locales": "fr",
}

STEPPER_URL = f"{API}/anf/dossier-stepper"
FRISE_URL = f"{API}/anf/usager/dossiers/frise-stepper"
NOTIFICATIONS_URL = f"{API}/notifications"
DETAILS_URL = f"{API}/anf/usager/dossiers/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": f"{BASE}/usagers/",
}

FORM_ACTION_RE = re.compile(r'<form[^>]*id="kc-form-login"[^>]*action="([^"]+)"')
KC_ERROR_RE = re.compile(r'id="input-error[^"]*"[^>]*>\s*([^<]+?)\s*<')


class AnefAuthError(Exception):
    """Login refusé (identifiants invalides, mot de passe à renouveler, formulaire introuvable, etc.)."""


class AnefClient:
    def __init__(self, login: str, password: str, timeout: float = 20.0):
        self._login = login
        self._password = password
        self._client = httpx.Client(headers=HEADERS, timeout=timeout, follow_redirects=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._client.close()

    def login(self):
        resp = self._client.get(SSO_AUTH_URL, params=AUTHORIZE_PARAMS)
        match = FORM_ACTION_RE.search(resp.text)
        if not match:
            raise AnefAuthError(f"Formulaire de connexion Keycloak introuvable (HTTP {resp.status_code}).")
        action_url = html.unescape(match.group(1))

        resp = self._client.post(
            action_url,
            data={"username": self._login, "password": self._password, "credentialId": ""},
            follow_redirects=False,
        )

        code = None
        hops = 0
        while resp.is_redirect and hops < 10:
            location = resp.headers.get("location", "")
            if "#" in location and "code=" in location.split("#", 1)[1]:
                fragment = location.split("#", 1)[1]
                params = dict(p.split("=", 1) for p in fragment.split("&") if "=" in p)
                code = unquote(params.get("code", ""))
                break
            resp = self._client.get(location, follow_redirects=False)
            hops += 1

        if not code:
            if resp.status_code == 200:
                err = KC_ERROR_RE.search(resp.text)
                raise AnefAuthError(html.unescape(err.group(1).strip()) if err else "Identifiants refusés par Keycloak.")
            raise AnefAuthError(f"Code d'autorisation introuvable (HTTP {resp.status_code}).")

        resp = self._client.post(TOKEN_EXCHANGE_URL, json={"code": code, "uri": REDIRECT_URI})
        if resp.status_code != 200:
            raise AnefAuthError(f"Échange du code refusé : HTTP {resp.status_code}: {resp.text[:300]}")

    def _get_json(self, url: str):
        resp = self._client.get(url)
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except ValueError:
            return None

    def fetch_dossier_snapshot(self):
        """Réplique fetchDossierData() de l'extension : renvoie un dict brut
        {statut_raw, frise, notifications, numero_decret, id, date_statut}
        ou None si le dossier n'est pas exploitable (ex: pas encore de dossier)."""
        stepper = self._get_json(STEPPER_URL)
        dossier = (stepper or {}).get("dossier") if stepper else None
        if not dossier or not dossier.get("statut"):
            return None

        frise_raw = self._get_json(FRISE_URL) or {}
        frise_data = frise_raw.get("data", frise_raw) if isinstance(frise_raw, dict) else {}
        frise = {
            "id_active": frise_data.get("id_active"),
            "type_frise": frise_data.get("type_frise"),
            "has_step_scec": frise_data.get("has_step_scec"),
        }

        notif_raw = self._get_json(NOTIFICATIONS_URL) or {}
        notifications = notif_raw.get("_items") or notif_raw.get("items") or notif_raw.get("data") or []

        numero_decret = None
        dossier_id = dossier.get("id")
        if dossier_id:
            detail_raw = self._get_json(DETAILS_URL + str(dossier_id)) or {}
            detail = detail_raw.get("data", detail_raw) if isinstance(detail_raw, dict) else {}
            try:
                idents = detail.get("demande", {}).get("informations", {}).get("etat_civil", {}).get("identites_decrets", [])
                for it in idents or []:
                    if it.get("decret", {}).get("id"):
                        numero_decret = str(it["decret"]["id"])
                        break
            except AttributeError:
                pass

        return {
            "statut_raw": dossier.get("statut"),
            "frise": frise,
            "notifications": notifications,
            "numero_decret": numero_decret,
            "id": dossier_id,
            "date_statut": dossier.get("date_statut"),
        }
