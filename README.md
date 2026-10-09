# anef-notifier

Vérifie périodiquement le statut de votre dossier de naturalisation ANEF et
envoie une notification Discord à chaque changement.

Logique de statut portée depuis l'extension Chrome "ANEF Status Tracker".
Contrairement à l'extension, ce script n'utilise pas de navigateur : il
appelle directement l'API ANEF avec vos identifiants.

## Installation

```bash
uv sync
```

## Configuration

Éditez `.env` (déjà créé depuis `.env.example`) :

```
ANEF_LOGIN=votre numéro de visa / titre de séjour
ANEF_PASSWORD=votre mot de passe ANEF
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
CHECK_SCHEDULE=30
```

Pour créer un webhook Discord : Paramètres du serveur → Intégrations →
Webhooks → Nouveau webhook → Copier l'URL.

`CHECK_SCHEDULE` accepte :
- un **nombre de minutes** : `CHECK_SCHEDULE=30` (vérifie toutes les 30 min)
- ou une **expression cron à 5 champs** : `CHECK_SCHEDULE=0 8-20 * * *`
  (toutes les heures entre 8h et 20h), `CHECK_SCHEDULE=*/15 9-18 * * 1-5`
  (toutes les 15 min, 9h-18h, du lundi au vendredi), etc.

**Le mot de passe est stocké en clair dans `.env`** (fichier gitignored).
Ne le committez jamais, et gardez ce fichier sur une machine de confiance.

## Lancement

```bash
uv run python main.py                # boucle en continu (planification CHECK_SCHEDULE)
uv run python main.py --once         # une seule vérification, puis quitte
uv run python main.py --status       # affiche le dernier état connu (pas d'appel réseau)
uv run python main.py --test-login   # teste la connexion ANEF + affiche le statut courant
uv run python main.py --test-webhook # envoie un message de test au webhook Discord
uv run python main.py --reset        # efface state.json (repart de zéro)
```

Le dernier statut connu est gardé dans `state.json` (créé automatiquement) :
une notification Discord n'est envoyée que lors d'un changement réel de
statut, pas à chaque vérification. Ce fichier contient :

```json
{
  "statutCode": "...",         // code de statut interne (status_data.py)
  "dateStatut": "...",         // date à laquelle ANEF a changé le statut
  "lastChangedAt": "...",      // quand CE script a détecté le changement
  "lastCheckedAt": "...",      // dernière vérification (changement ou non)
  "lastErrorKey": "...",       // problème en cours (null si tout va bien)
  "lastErrorAt": "..."         // quand ce problème est apparu
}
```

Chaque notification Discord de changement indique aussi le statut précédent,
la date du changement côté ANEF (« Statut depuis le ») et l'heure de la
vérification (pied de page). Note : après un `--reset`, la vérification
suivante traite le statut courant comme un « premier changement » et envoie
donc une notification même si rien n'a réellement changé côté ANEF.

## Logs et gestion des erreurs

Chaque exécution écrit dans `anef-notifier.log` (créé automatiquement, à côté
de `state.json`), en plus de la sortie standard. Ce fichier est tronqué aux
`LOG_MAX_LINES` dernières lignes (def. 5000) à chaque écriture : il ne grossit
donc jamais indéfiniment sur un service qui tourne en continu.

Un problème (échec de connexion ANEF, erreur réseau, API ANEF qui ne renvoie
rien d'exploitable...) est traité comme un **état**, au même titre que le
statut du dossier : il est enregistré dans `state.json` (`lastErrorKey`) et
n'envoie une alerte Discord qu'à son **apparition**, pas à chaque vérification
suivante tant qu'il persiste — sinon une panne de plusieurs heures spamerait
un message toutes les `CHECK_SCHEDULE`. Dès que la vérification suivante
réussit, un message « ✅ Rétabli » est envoyé une seule fois et l'état est
nettoyé. `--status` affiche un problème en cours s'il y en a un.

## Limites connues

- L'API ANEF n'est pas documentée officiellement : le flow de connexion
  (SSO Keycloak `anef-usagers` : page de login → code d'autorisation →
  `POST /api/keycloak/token`) et la logique de statut ont été reconstitués en
  observant le trafic réel du site et de l'extension. Un changement côté ANEF
  (ex. structure du formulaire Keycloak) peut casser le script.
- Pas de garde-fou anti-régression (contrairement à l'extension) : si l'API
  renvoie ponctuellement un statut en retrait, une (fausse) notification de
  recul peut partir. En pratique, rare.
- Si le processus lui-même s'arrête (crash, redémarrage du serveur, session
  tmux tuée), rien ne le relance automatiquement : ni systemd, ni cron. À
  surveiller si le script tourne sans supervision sur un serveur.
