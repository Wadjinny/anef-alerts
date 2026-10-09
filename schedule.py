"""
Planification des vérifications : CHECK_SCHEDULE accepte soit un
nombre de minutes (ex: "30"), soit une expression cron à 5 champs
(ex: "*/30 * * * *", "0 8-20 * * *" pour une vérification horaire entre 8h et
20h). Le choix se fait simplement en essayant de parser la valeur comme un
nombre ; si ça échoue, on la traite comme une expression cron.
"""

from datetime import datetime

from croniter import croniter, CroniterBadCronError


def is_cron_expression(raw: str) -> bool:
    try:
        float(raw)
        return False
    except ValueError:
        return True


def validate_schedule(raw: str):
    """Lève une ValueError avec un message clair si `raw` n'est ni un nombre
    de minutes ni une expression cron valide."""
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("CHECK_SCHEDULE est vide.")
    if not is_cron_expression(raw):
        return
    try:
        croniter(raw)
    except (CroniterBadCronError, ValueError) as e:
        raise ValueError(
            f"CHECK_SCHEDULE={raw!r} n'est ni un nombre de minutes, "
            f"ni une expression cron valide à 5 champs : {e}"
        )


def describe_schedule(raw: str) -> str:
    raw = raw.strip()
    if is_cron_expression(raw):
        return f"cron \"{raw}\""
    return f"toutes les {float(raw):g} min"


def next_run_after(raw: str, now: datetime) -> datetime:
    """Date du prochain run après `now`, pour affichage uniquement
    (sleep_seconds_until recalcule indépendamment)."""
    raw = raw.strip()
    if is_cron_expression(raw):
        return croniter(raw, now).get_next(datetime)
    from datetime import timedelta
    return now + timedelta(minutes=float(raw))


def sleep_seconds_until_next(raw: str, now: datetime) -> float:
    raw = raw.strip()
    if is_cron_expression(raw):
        next_run = croniter(raw, now).get_next(datetime)
        return max(0.0, (next_run - now).total_seconds())
    return float(raw) * 60
