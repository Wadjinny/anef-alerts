"""
Recombine les signaux bruts de l'API ANEF (statut macro + frise + notifications)
en un statut interne lisible. Porté (version simplifiée) depuis l'extension
ANEF Status Tracker (lib/anef-mapper.js) : on garde la logique de dérivation du
statut, mais pas les garde-fous anti-régression (qui dépendent d'un historique
local que ce script n'a pas besoin de maintenir).
"""

FRISE_TYPE_KEYS = {
    "DECISION_PLATEFORME_AVANT_VF": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "traitement_instruction", 4: "decision_prefecture"},
    "DECISION_PLATEFORME_AVANT_RECEPISSE_COMPLETUDE": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "decision_prefecture"},
    "DECISION_PLATEFORME_AVANT_EA": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "decision_prefecture"},
    "DECISION_PLATEFORME_APRES_EA": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "entretien_assimilation", 8: "traitement_plateforme_3", 9: "decision_prefecture"},
    "DECISION_SDANF_AVANT_SCEC": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "entretien_assimilation", 8: "traitement_plateforme_3", 9: "traitement_sdanf_1", 10: "decision_prise"},
    "DECISION_SDANF_APRES_SCEC": {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "entretien_assimilation", 8: "traitement_plateforme_3", 9: "traitement_sdanf_1", 10: "traitement_scec", 11: "traitement_sdanf_2", 12: "decision_prise"},
}

COMPLET_SANS_SCEC = {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "entretien_assimilation", 8: "traitement_plateforme_3", 9: "traitement_sdanf_1", 10: "decision_prise", 11: "ceremonie_naturalisation"}
COMPLET_AVEC_SCEC = {0: "demande_envoyee", 1: "demande_envoyee", 2: "examen_pieces", 3: "demande_deposee", 4: "traitement_instruction", 5: "recepisse_completude", 6: "traitement_instruction_2", 7: "entretien_assimilation", 8: "traitement_plateforme_3", 9: "traitement_sdanf_1", 10: "traitement_scec", 11: "traitement_sdanf_2", 12: "decision_prise", 13: "ceremonie_naturalisation"}

FRISE_KEY_TO_STATUT = {
    "demande_envoyee": "dossier_depose",
    "examen_pieces": "verification_formelle_en_cours",
    "demande_deposee": "instruction_a_affecter",
    "traitement_instruction": "instruction_recepisse_completude_a_envoyer",
    "traitement_instruction_2": "instruction_date_ea_a_fixer",
    "recepisse_completude": "instruction_date_ea_a_fixer",
    "entretien_assimilation": "ea_en_attente_ea",
    "traitement_plateforme_3": "prop_decision_pref_a_effectuer",
    "traitement_sdanf_1": "controle_sdanf",
    "traitement_scec": "controle_en_attente_pec",
    "traitement_sdanf_2": "controle_en_attente_retour_hierarchique",
    "ceremonie_naturalisation": "decret_naturalisation_publie",
}

MACRO_STATUS_TO_CODE = {
    "DEMANDE_EN_COURS_DE_TRAITEMENT": "instruction_recepisse_completude_a_envoyer",
    "DECISION_FAVORABLE": "controle_transmise_pour_decret",
    "DEMANDE_FAVORABLE": "controle_transmise_pour_decret",
    "DECISION_DEFAVORABLE": "decision_negative_en_delais_recours",
    "DEMANDE_REJETEE": "decision_negative_en_delais_recours",
    "DEMANDE_AJOURNEE": "decision_notifiee",
    "DEMANDE_CLASSEE_SANS_SUITE": "css_notifie",
    "DEMANDE_IRRECEVABLE": "irrecevabilite_manifeste",
    "DECRET_PUBLIE": "decret_naturalisation_publie",
    "DECRET_NATURALISATION_PUBLIE": "decret_naturalisation_publie",
    "NATURALISATION_PUBLIEE": "decret_naturalisation_publie",
    "DECISION_NOTIFIEE": "decision_notifiee",
    "DEMANDE_TRAITEE": "demande_traitee",
}

TERMINAL_MACROS = {
    "DECISION_NOTIFIEE", "DECISION_DEFAVORABLE", "DEMANDE_REJETEE", "DEMANDE_AJOURNEE",
    "DEMANDE_CLASSEE_SANS_SUITE", "DEMANDE_IRRECEVABLE", "DEMANDE_TRAITEE", "DECRET_PUBLIE",
}
POST_DECISION_FRISE_KEYS = {"decision_prefecture", "decision_prise", "ceremonie_naturalisation"}
DECISION_MACROS = {"DECISION_FAVORABLE", "DEMANDE_FAVORABLE"}
DECISION_MOTIFS = {"DECISION_FAVORABLE", "DECISION_DEFAVORABLE", "DECRET_PUBLIE", "CLASSEMENT_SANS_SUITE"}

MOTIF_CODE = {
    "CONFIRMATION_DEPOT": "dossier_depose",
    "RECEPISSE_DEPOT_ENVOYE": "instruction_a_affecter",
    "RECEPISSE_COMPLETUDE_ENVOYE": "instruction_date_ea_a_fixer",
    "ENTRETIEN_ASSIMILATION_FIXE": "ea_en_attente_ea",
    "ENTRETIEN_ASSIMILATION_REPORTE": "ea_demande_report_ea",
    "DECISION_FAVORABLE": "controle_transmise_pour_decret",
    "DECISION_DEFAVORABLE": "decision_negative_en_delais_recours",
    "DECRET_PUBLIE": "decret_naturalisation_publie",
    "CLASSEMENT_SANS_SUITE": "css_notifie",
    "MISE_EN_DEMEURE": "verification_formelle_mise_en_demeure",
}


def get_frise_step_keys(type_frise, has_step_scec):
    t = (type_frise or "").strip().upper()
    if t == "DECISION_RAPO":
        return {}
    if t in FRISE_TYPE_KEYS:
        return FRISE_TYPE_KEYS[t]
    if t == "COMPLET" and has_step_scec is False:
        return COMPLET_SANS_SCEC
    return COMPLET_AVEC_SCEC


def frise_key_to_statut_code(frise_key, ctx):
    if frise_key == "decision_prefecture":
        return "decision_notifiee" if ctx.get("decisionAvailable") else "prop_decision_pref_a_effectuer"
    if frise_key == "decision_prise":
        if ctx.get("inDecretPipeline"):
            return "prete_pour_insertion_decret"
        if ctx.get("decisionAvailable"):
            return "decision_notifiee"
        return "controle_en_attente_retour_hierarchique"
    return FRISE_KEY_TO_STATUT.get(frise_key)


def parse_statut_field(statut):
    if isinstance(statut, dict):
        raw = statut.get("type") or statut.get("code") or statut.get("value") or statut.get("statut") or ""
    else:
        raw = statut or ""
    raw = str(raw).strip()
    try:
        from urllib.parse import unquote
        raw = unquote(raw)
    except Exception:
        pass
    tokens = [t.strip() for t in raw.split("|") if t.strip()]
    macro = (tokens.pop(0).upper() if tokens else "")
    flags = [t.upper() for t in tokens if "." not in t]
    return macro, flags


def interpret_flags(flags):
    has = lambda f: f in flags
    return {
        "decisionAvailable": has("SHOW_DECISION_DOWNLOAD_BUTTON"),
        "inDecretPipeline": has("CAN_ACCESS_DESISTEMENT_NAT_DECRET") or has("CAN_ACCESS_DESISTEMENT_NAT"),
        "canRapo": any("RAPO" in f for f in flags),
        "dossierCompleted": has("STATUT_DOSSIER_COMPLETED"),
    }


def is_decree_published_macro(macro):
    m = (macro or "").upper()
    return "PUBLI" in m and ("DECRET" in m or "NATURALISATION" in m)


def build_timeline(notifications, dossier_id):
    items = notifications if isinstance(notifications, list) else (notifications or {}).get("_items") or (notifications or {}).get("items") or []
    want_id = str(dossier_id) if dossier_id is not None else None
    out = []
    for n in items:
        if str((n.get("type_notification") or "")).upper() != "NATIONALITE":
            continue
        if want_id is not None and str(n.get("id_demande")) != want_id:
            continue
        motif = str(n.get("motif_notification") or "").upper()
        date = n.get("_created") or n.get("date_creation") or n.get("date")
        if not date:
            continue
        out.append({"date": date, "motif": motif, "code": MOTIF_CODE.get(motif)})
    out.sort(key=lambda e: str(e["date"]))
    return out


def derive_status(statut=None, frise=None, notifications=None, dossier_id=None, numero_decret=None):
    """Retourne un dict { statutCode, derivedFrom, macro, friseKey, decretAssigned }."""
    macro, flags = parse_statut_field(statut)
    flag_info = interpret_flags(flags)
    timeline = build_timeline(notifications, dossier_id)

    frise_key = None
    frise = frise or {}
    id_active = frise.get("id_active")
    if isinstance(id_active, (int, float)) or (isinstance(id_active, str) and id_active.strip() != ""):
        try:
            id_active = int(id_active)
            if id_active >= 0:
                keys = get_frise_step_keys(frise.get("type_frise"), frise.get("has_step_scec"))
                frise_key = keys.get(id_active)
        except (TypeError, ValueError):
            pass

    decret_assigned = numero_decret is not None and str(numero_decret).strip() != ""

    dernier = timeline[-1] if timeline else None
    decision_corroboree = (
        frise_key is None
        or frise_key in POST_DECISION_FRISE_KEYS
        or decret_assigned
        or flag_info["dossierCompleted"]
        or macro in TERMINAL_MACROS
        or macro in DECISION_MACROS
        or is_decree_published_macro(macro)
        or (dernier is not None and dernier["motif"] in DECISION_MOTIFS)
    )
    decision_available = decision_corroboree and flag_info["decisionAvailable"]
    in_decret_pipeline = decision_corroboree and flag_info["inDecretPipeline"]

    ctx = {"inDecretPipeline": in_decret_pipeline, "decisionAvailable": decision_available}

    frise_code = frise_key_to_statut_code(frise_key, ctx) if frise_key else None
    macro_code = MACRO_STATUS_TO_CODE.get(macro)
    timeline_code = timeline[-1]["code"] if timeline else None

    derived_from = "frise" if frise_code else ("macro" if macro_code else ("timeline" if timeline_code else None))
    statut_code = frise_code or macro_code or timeline_code

    if decision_available and in_decret_pipeline and frise_key == "decision_prise":
        statut_code, derived_from = "inseree_dans_decret", "signal"

    published_terminal = {"decret_naturalisation_publie", "decret_naturalisation_publie_jo", "decret_publie", "demande_traitee"}
    if decret_assigned and statut_code not in published_terminal:
        statut_code = "decret_naturalisation_publie" if frise_key == "ceremonie_naturalisation" else "inseree_dans_decret"
        derived_from = "signal"

    published_event = any(e["motif"] == "DECRET_PUBLIE" for e in timeline)

    if flag_info["dossierCompleted"] and decret_assigned:
        statut_code, derived_from = "decret_naturalisation_publie", "signal"
    elif flag_info["dossierCompleted"] and macro in TERMINAL_MACROS:
        statut_code = MACRO_STATUS_TO_CODE.get(macro, statut_code)
        derived_from = "signal"

    if is_decree_published_macro(macro) or published_event:
        statut_code, derived_from = "decret_naturalisation_publie", "signal"

    return {
        "statutCode": statut_code,
        "derivedFrom": derived_from,
        "macro": macro,
        "flags": flags,
        "friseKey": frise_key,
        "decretAssigned": decret_assigned,
        "timeline": timeline,
    }
