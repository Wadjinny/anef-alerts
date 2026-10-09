"""
Dictionnaire des statuts ANEF, porté depuis l'extension ANEF Status Tracker
(lib/status-parser.js) pour obtenir un libellé humain à partir d'un code
de statut interne.
"""

STATUTS = {
    "draft": {"phase": "Brouillon", "explication": "Dossier en brouillon", "etape": 1, "icon": "📝"},
    "dossier_depose": {"phase": "Dépôt", "explication": "Dossier déposé", "etape": 2, "icon": "📨"},
    "verification_formelle_a_traiter": {"phase": "Vérification formelle", "explication": "Dossier reçu, en tri", "etape": 3, "icon": "🔍"},
    "verification_formelle_en_cours": {"phase": "Vérification formelle", "explication": "Tri en cours", "etape": 3, "icon": "🔍"},
    "verification_formelle_mise_en_demeure": {"phase": "Vérification formelle", "explication": "Mise en demeure, pièces à fournir", "etape": 3, "icon": "⚠️"},
    "css_mise_en_demeure_a_affecter": {"phase": "Vérification formelle", "explication": "Classement sans suite en cours", "etape": 3, "icon": "⚠️"},
    "css_mise_en_demeure_a_rediger": {"phase": "Vérification formelle", "explication": "Classement sans suite en rédaction", "etape": 3, "icon": "⚠️"},
    "instruction_a_affecter": {"phase": "Affectation", "explication": "Dossier recevable, attente d'affectation", "etape": 4, "icon": "👤"},
    "instruction_recepisse_completude_a_envoyer": {"phase": "Instruction", "explication": "Dossier complet, examen approfondi", "etape": 5, "icon": "📖"},
    "instruction_recepisse_completude_a_envoyer_retour_complement_a_traiter": {"phase": "Instruction", "explication": "Compléments reçus, à vérifier", "etape": 5, "icon": "📋"},
    "css_manuels_a_affecter": {"phase": "Classement sans suite", "explication": "Proposition de CSS manuel, à affecter", "etape": 5, "icon": "⚠️"},
    "css_manuels_a_rediger": {"phase": "Classement sans suite", "explication": "CSS manuel, rédaction en cours", "etape": 5, "icon": "⚠️"},
    "css_automatiques_a_affecter": {"phase": "Classement sans suite", "explication": "Proposition de CSS automatique, à affecter", "etape": 5, "icon": "⚠️"},
    "css_automatiques_a_rediger": {"phase": "Classement sans suite", "explication": "CSS automatique, rédaction en cours", "etape": 5, "icon": "⚠️"},
    "instruction_date_ea_a_fixer": {"phase": "Complétude & enquêtes", "explication": "Enquêtes administratives lancées", "etape": 6, "icon": "🔎"},
    "ea_demande_report_ea": {"phase": "Complétude & enquêtes", "explication": "Demande de report d'entretien", "etape": 6, "icon": "🔄"},
    "ea_en_attente_ea": {"phase": "Entretien d'assimilation", "explication": "Convocation envoyée, en attente", "etape": 7, "icon": "📬"},
    "ea_crea_a_valider": {"phase": "Entretien d'assimilation", "explication": "Entretien passé, compte-rendu en rédaction", "etape": 7, "icon": "✅"},
    "prop_decision_pref_a_effectuer": {"phase": "Décision préfecture", "explication": "Avis préfectoral en cours", "etape": 8, "icon": "⚖️"},
    "prop_decision_pref_en_attente_retour_hierarchique": {"phase": "Décision préfecture", "explication": "Validation hiérarchique en cours", "etape": 8, "icon": "👔"},
    "prop_decision_pref_prop_a_editer": {"phase": "Décision préfecture", "explication": "Rédaction de la proposition", "etape": 8, "icon": "📝"},
    "prop_decision_pref_en_attente_retour_signataire": {"phase": "Décision préfecture", "explication": "Attente signature du préfet", "etape": 8, "icon": "✍️"},
    "controle_sdanf": {"phase": "Contrôle SDANF", "explication": "Contrôle ministériel SDANF", "etape": 9, "icon": "🏛️"},
    "controle_a_affecter": {"phase": "Contrôle SDANF", "explication": "Arrivé à la SDANF, attente affectation", "etape": 9, "icon": "🏛️"},
    "controle_a_effectuer": {"phase": "Contrôle SDANF", "explication": "Contrôle ministériel en cours", "etape": 9, "icon": "📑"},
    "controle_en_attente_pec": {"phase": "Contrôle SCEC", "explication": "Transmis au SCEC de Nantes", "etape": 9, "icon": "🏛️"},
    "controle_pec_a_faire": {"phase": "Contrôle SCEC", "explication": "Vérification d'état civil en cours", "etape": 9, "icon": "✔️"},
    "controle_transmise_pour_decret": {"phase": "Préparation décret", "explication": "Avis FAVORABLE, transmis pour décret", "etape": 10, "icon": "🎉"},
    "controle_en_attente_retour_hierarchique": {"phase": "Préparation décret", "explication": "Validation hiérarchique ministérielle", "etape": 10, "icon": "👔"},
    "controle_decision_a_editer": {"phase": "Préparation décret", "explication": "Décision favorable, édition en cours", "etape": 10, "icon": "📄"},
    "controle_en_attente_signature": {"phase": "Préparation décret", "explication": "Attente signature ministérielle", "etape": 10, "icon": "✍️"},
    "transmis_a_ac": {"phase": "Préparation décret", "explication": "Transmis à l'administration centrale", "etape": 10, "icon": "📬"},
    "a_verifier_avant_insertion_decret": {"phase": "Préparation décret", "explication": "Vérifications finales avant insertion", "etape": 10, "icon": "🔎"},
    "prete_pour_insertion_decret": {"phase": "Préparation décret", "explication": "Validé, prêt pour insertion au décret", "etape": 10, "icon": "✅"},
    "decret_en_preparation": {"phase": "Préparation décret", "explication": "Décret en cours de préparation", "etape": 10, "icon": "📋"},
    "decret_a_qualifier": {"phase": "Préparation décret", "explication": "Décret en cours de qualification", "etape": 10, "icon": "📋"},
    "decret_en_validation": {"phase": "Préparation décret", "explication": "Décret en validation finale", "etape": 10, "icon": "📋"},
    "inseree_dans_decret": {"phase": "Publication JO", "explication": "Inséré dans un décret signé", "etape": 11, "icon": "🎉"},
    "decret_envoye_prefecture": {"phase": "Publication JO", "explication": "Décret envoyé à votre préfecture", "etape": 11, "icon": "📨"},
    "notification_envoyee": {"phase": "Publication JO", "explication": "Notification officielle envoyée", "etape": 11, "icon": "📬"},
    "decret_naturalisation_publie": {"phase": "NATURALISÉ(E)", "explication": "Décret publié au Journal Officiel", "etape": 12, "icon": "🏅"},
    "decret_naturalisation_publie_jo": {"phase": "NATURALISÉ(E)", "explication": "Décret publié au Journal Officiel", "etape": 12, "icon": "🏅"},
    "decret_publie": {"phase": "NATURALISÉ(E)", "explication": "Décret publié", "etape": 12, "icon": "🏅"},
    "demande_traitee": {"phase": "Finalisé", "explication": "Demande entièrement traitée", "etape": 12, "icon": "✅"},
    "decision_negative_en_delais_recours": {"phase": "Décision négative", "explication": "Défavorable, délai de recours ouvert", "etape": 12, "icon": "❌"},
    "decision_notifiee": {"phase": "Décision négative", "explication": "Décision notifiée au demandeur", "etape": 12, "icon": "❌"},
    "demande_en_cours_rapo": {"phase": "Recours RAPO", "explication": "Recours administratif en cours", "etape": 12, "icon": "⚖️"},
    "controle_demande_notifiee": {"phase": "Décision notifiée", "explication": "Décision de contrôle notifiée", "etape": 12, "icon": "📬"},
    "irrecevabilite_manifeste": {"phase": "Irrecevabilité", "explication": "Conditions légales non remplies", "etape": 12, "icon": "❌"},
    "irrecevabilite_manifeste_en_delais_recours": {"phase": "Irrecevabilité", "explication": "Irrecevable, délai de recours ouvert", "etape": 12, "icon": "❌"},
    "css_en_delais_recours": {"phase": "Classement sans suite", "explication": "Classé sans suite, recours possible", "etape": 12, "icon": "⚠️"},
    "css_notifie": {"phase": "Classement sans suite", "explication": "Classement sans suite notifié", "etape": 12, "icon": "⚠️"},
}


def get_status_explanation(statut_code):
    code = (statut_code or "").lower().strip()
    info = STATUTS.get(code)
    if info:
        return {**info, "found": True, "code": code}
    return {
        "phase": "Statut inconnu",
        "explication": statut_code or "Non disponible",
        "etape": 0,
        "icon": "❓",
        "found": False,
        "code": code,
    }
