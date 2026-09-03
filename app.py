# -*- coding: utf-8 -*-
"""
NSIA Assurances Togo - Call Center Dashboard
Application Streamlit pour la saisie, le suivi et l'analyse des appels.
Base collaborative: base PostgreSQL Supabase.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import hashlib
import hmac
import io
import json
import time

from points_de_vente import POINTS_DE_VENTE as DEFAULT_POINTS_DE_VENTE
from database_service import (
    DatabaseConfigurationError,
    DatabaseError,
    DatabaseService,
    values_for_type,
)

# ============================================================================
# CONFIGURATION & THEME
# ============================================================================

NSIA = {
    "navy": "#202C54",
    "gold": "#CF9A06",
    "white": "#FFFFFF",
    "silver": "#ACA38B",
    "dark_gray": "#605C57",
    "blue_black": "#0D1222",
    "light_bg": "#F5F5F7",
    "card_bg": "#FFFFFF",
    "border": "#E0E0E3",
    "text_primary": "#202C54",
    "text_secondary": "#605C57",
    "success": "#2E7D32",
    "error": "#C62828",
    "warning": "#F9A825",
}

st.set_page_config(
    page_title="NSIA Call Center",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
/* Base */
.stApp {{
    background-color: {NSIA['blue_black']};
    color: {NSIA['silver']};
    font-family: 'Segoe UI', 'Inter', Roboto, sans-serif;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NSIA['navy']} 0%, {NSIA['blue_black']} 100%);
    color: {NSIA['white']};
}}
section[data-testid="stSidebar"] .stRadio > label,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stMarkdown {{
    color: {NSIA['white']} !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {NSIA['gold']} !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(207,154,6,0.25);
}}

/* Typography */
h1, h2, h3, h4, h5 {{
    color: {NSIA['white']};
    font-weight: 600;
    letter-spacing: -0.005em;
}}
h1 {{ font-size: 1.75rem; }}
h2 {{ font-size: 1.35rem; }}
h3 {{ font-size: 1.1rem; }}

/* Cartes / formulaires */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stForm"]) {{
    background-color: rgba(13,18,34,0.75);
    padding: 1.1rem 1.25rem;
    border-radius: 0.9rem;
    border: 1px solid rgba(172,163,139,0.15);
    box-shadow: 0 1px 6px rgba(0,0,0,0.35);
    margin-top: 0.6rem;
}}
div[data-testid="stHorizontalBlock"] > div {{
    gap: 0.65rem;
}}

/* Métriques */
div[data-testid="stMetric"] {{
    background-color: rgba(32,44,84,0.35);
    padding: 0.9rem 1.1rem;
    border-radius: 0.8rem;
    border-left: 3px solid {NSIA['gold']};
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}}
div[data-testid="stMetric"] label {{
    color: {NSIA['silver']};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: {NSIA['white']};
    font-weight: 700;
    font-size: 1.25rem;
}}

/* Boutons */
button[kind="primary"] {{
    background-color: {NSIA['gold']};
    color: {NSIA['navy']};
    border: none;
    border-radius: 0.5rem;
    padding: 0.65rem 0.9rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    box-shadow: 0 1px 5px rgba(207,154,6,0.25);
}}
button[kind="primary"]:hover {{
    background-color: #b8850a;
}}
button[kind="secondary"] {{
    background-color: rgba(255,255,255,0.08);
    color: {NSIA['white']};
    border: 1px solid rgba(172,163,139,0.35);
    border-radius: 0.5rem;
    padding: 0.65rem 0.9rem;
    font-weight: 600;
}}
button[kind="secondary"]:hover {{
    background-color: rgba(255,255,255,0.13);
    border-color: {NSIA['silver']};
}}

/* Chips campagne */
.chip {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.55rem 0.9rem;
    border-radius: 999px;
    border: 1px solid {NSIA['gold']};
    background: {NSIA['gold']};
    color: {NSIA['dark_gray']};
    font-weight: 700;
    transition: all 0.2s ease;
    margin: 0.2rem 0.3rem 0.2rem 0;
    font-size: 0.92rem;
    cursor: pointer;
    user-select: none;
}}
.chip:hover {{
    background-color: #b8850a;
    border-color: #b8850a;
    color: {NSIA['navy']};
}}
.chip.active {{
    background-color: {NSIA['navy']};
    color: {NSIA['white']};
    border-color: {NSIA['gold']};
    box-shadow: 0 1px 6px rgba(32,44,84,0.35);
}}

/* Dataframe */
div[data-testid="stDataFrame"] {{
    border-radius: 0.8rem;
    overflow: hidden;
    border: 1px solid rgba(172,163,139,0.25);
    background-color: rgba(13,18,34,0.6);
}}

/* Inputs */
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stDateInput"] > div,
div[data-testid="stTimeInput"] > div,
div[data-testid="stNumberInput"] > div,
div[data-testid="stTextArea"] textarea {{
    border-radius: 0.45rem !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.4rem;
    border-bottom: 1px solid {NSIA['border']};
}}
.stTabs [data-baseweb="tab"] {{
    color: {NSIA['text_secondary']};
    font-weight: 600;
    padding: 0.5rem 0.9rem;
    border-radius: 0.5rem 0.5rem 0 0;
}}
.stTabs [aria-selected="true"] {{
    color: {NSIA['navy']};
    background: {NSIA['white']};
    border-bottom: 2px solid {NSIA['gold']};
}}

/* Alerts / expander */
.stAlert {{
    border-radius: 0.6rem;
    border-left: 3px solid {NSIA['gold']};
    background-color: rgba(13,18,34,0.75);
    color: {NSIA['silver']};
}}
div[data-testid="stExpander"] {{
    border: 1px solid rgba(172,163,139,0.25);
    border-radius: 0.65rem;
    background-color: rgba(13,18,34,0.65);
    color: {NSIA['silver']};
}}

/* Separator */
hr {{
    border: none;
    border-top: 1px solid {NSIA['border']};
    margin: 1rem 0;
}}

/* Responsive */
@media (max-width: 768px) {{
    h1 {{ font-size: 1.4rem; }}
    h2 {{ font-size: 1.15rem; }}
    div[data-testid="stMetric"] {{
        padding: 0.7rem;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

DATA_SOURCE_LABEL = "Base en ligne Supabase — appels_call_center"

# ============================================================================
# DONNÉES NSIA
# ============================================================================

DEFAULT_CAMPAIGNS = ["SATURATION", "RELANCE", "RECUPERATION", "ONBOARDING", "RECEPTION"]
DEFAULT_PRISE_APPEL = ["Oui", "Non", "Injoignable"]
DEFAULT_PRODUCTS = [
    "AUTRES DOMMAGES AUX BIENS",
    "AUTOMOBILE",
    "BRIS DE MACHINES",
    "COMPLEMENTAIRE ACCIDENT DE TRAVAIL",
    "DOMMAGES CORPORELS",
    "FACULTES",
    "GLOBALE BANQUE",
    "GLOBALE DOMMAGES",
    "INDIVIDUELLE ACCIDENT GROUPE",
    "INDIVIDUELLE ACCIDENTS (GRPE RD)",
    "INDIVIDUELLE ACCIDENTS PARTICULIER",
    "INDIVIDUELLE VOYAGE",
    "INCENDIE RISQUES COMMERCIAUX",
    "INCENDIE RISQUES SIMPLES",
    "INDIVIDUELLE ACCIDENTS",
    "MULTIRISQUE PROFESSIONNELLE",
    "MULTIRISQUE HABITATION",
    "RC BICYCLETTE",
    "RC ASSOCIATIONS SPORTIVES",
    "RC CHEF D ENTREPRISE",
    "RC COLONIES DE VACANCES",
    "RC CHEF DE FAMILLE",
    "RC DECENNALE",
    "RC EXPLOITATION",
    "RC ENTREPRISES BATIMENT ET GENIE CIVIL",
    "RC ENTREPRISES INDUSTRIELLES ET COMMERCIALES",
    "RC EXPLOITATION BATIMENT ET GENIE CIVIL",
    "RC ORGANISATION DE MANIFESTATIONS",
    "RC PROFESSIONNELLE",
    "RC PROFESSIONS MEDICALES ET PARA-MEDICALE",
    "RC PROPRIETAIRE D IMMEUBLE",
    "RC SCOLAIRE",
    "RESPONSABILITE CIVILE",
    "SANTE",
    "TOUS RISQUES CHANTIERS",
    "TOUS RISQUES INFORMATIQUE",
    "TOUS RISQUES MONTAGES",
    "VOL",
]
DEFAULT_MOUVEMENTS = ["REN", "AFN"]
DEFAULT_RESEAUX = [
    "AGENTS GENERAUX",
    "AUTRES COURTIERS",
    "BANCASSURANCE",
    "BUREAUX DIRECTS",
    "GCA",
    "GRAS SAVOYE",
    "LA PROTECTRICE",
    "OLEA INSURANCE SOLUTIONS",
]
DEFAULT_RECEPTIONS = list(DEFAULT_MOUVEMENTS)
DEFAULT_TO = ["Audrey", "Sylvanus", "Florentina"]

DEFAULT_STATUS = [
    "Repondu",
    "Non repondu - Occupe",
    "Non repondu - Pas de reponse",
    "Non repondu - Messagerie",
    "Annule",
    "Termine",
]
DEFAULT_MOTIFS = [
    "Occupe",
    "Pas de reponse",
    "Messagerie vocal",
    "Numero invalide",
    "Client indisponible",
    "Appel transfere",
    "Autre",
]

DEFAULT_POINTS_DE_VENTE = list(DEFAULT_POINTS_DE_VENTE)

DEFAULT_FEEDBACK = [
    "Barrage",
    "Aucun numero",
    "Rappel apres",
    "Injoignable",
    "Difficulter de communication",
    "Refus",
    "Stop appel",
    "Sinistre en cours",
]

# ============================================================================
# CODE D'ACCÈS ET DONNÉES SUPABASE
# ============================================================================


def _is_same_year(d, annee):
    try:
        return d.year == int(annee)
    except Exception:
        return False


def _is_same_year_month(d, annee, mois):
    try:
        return d.year == int(annee) and d.month == int(mois)
    except Exception:
        return False


def _is_same_iso_week(d, annee, semaine):
    try:
        iso = d.isocalendar()
        return int(iso.year) == int(annee) and int(iso.week) == int(semaine)
    except Exception:
        return False


def _secret_section(name):
    try:
        return dict(st.secrets[name])
    except (KeyError, TypeError):
        return {}


def authentifier_utilisateur():
    """Protège l'application par un code commun stocké dans les secrets."""
    application = _secret_section("application")
    access_required = bool(application.get("access_required", True))
    if not access_required:
        return {"name": "Développement local", "email": "local@localhost"}

    access_code = str(application.get("access_code", "")).strip()
    if not access_code:
        st.error(
            "Le code d'accès n'est pas configuré. Renseignez "
            "application.access_code dans les secrets Streamlit."
        )
        st.stop()
    if len(access_code) < 12:
        st.error(
            "Le code d'accès doit contenir au moins 12 caractères. "
            "Choisissez une phrase secrète difficile à deviner."
        )
        st.stop()

    if st.session_state.get("access_granted"):
        return {"name": "Utilisateur autorisé", "email": ""}

    now = time.time()
    locked_until = float(st.session_state.get("access_locked_until", 0))
    if locked_until > now:
        remaining = max(int(locked_until - now), 1)
        st.title("NSIA Call Center")
        st.error(f"Trop de tentatives. Réessayez dans {remaining} secondes.")
        st.stop()

    st.title("NSIA Call Center")
    st.info("Saisissez le code d'accès communiqué par votre responsable.")
    with st.form("access_form", clear_on_submit=True):
        submitted_code = st.text_input("Code d'accès", type="password")
        submitted = st.form_submit_button(
            "Accéder à l'application", type="primary", use_container_width=True
        )
    if submitted:
        if hmac.compare_digest(submitted_code, access_code):
            st.session_state["access_granted"] = True
            st.session_state["access_attempts"] = 0
            st.rerun()
        attempts = int(st.session_state.get("access_attempts", 0)) + 1
        st.session_state["access_attempts"] = attempts
        if attempts >= 5:
            st.session_state["access_locked_until"] = time.time() + 300
            st.session_state["access_attempts"] = 0
            st.error("Trop de tentatives. L'accès est bloqué pendant 5 minutes.")
        else:
            st.error("Code incorrect.")
    st.stop()


@st.cache_resource(show_spinner=False)
def get_database_service():
    configuration = _secret_section("database")
    return DatabaseService.from_mapping(configuration)


@st.cache_data(ttl=30, show_spinner=False)
def _charger_appels_cache():
    return get_database_service().list_calls()


@st.cache_data(ttl=60, show_spinner=False)
def _charger_references_cache(include_inactive=False):
    return get_database_service().list_references(include_inactive=include_inactive)


def invalider_cache_donnees():
    _charger_appels_cache.clear()
    _charger_references_cache.clear()


def lire_appels_base():
    columns = [
        "Date", "TO", "Nom du Client", "telephone", "Immatriculation",
        "Police", "Campagne", "Reception", "Prise d'appel",
        "Produit existant", "Produit proposé", "Feedback", "CA",
        "Point de vente", "Heure_appel", "Statut", "Motif_non_reponse",
        "Commentaire", "Satisfaction", "Recommendation", "Produit souhaite",
        "_item_id", "_etag",
    ]
    try:
        records = _charger_appels_cache()
        df = pd.DataFrame(records)
        for column in columns:
            if column not in df.columns:
                df[column] = None
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["CA"] = pd.to_numeric(df["CA"], errors="coerce").fillna(0)
        return df[columns]
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"Connexion à la base impossible : {exc}")
        return pd.DataFrame(columns=columns)


def _references_par_defaut():
    return {
        "campagnes": list(DEFAULT_CAMPAIGNS),
        "to": list(DEFAULT_TO),
        "produits": list(DEFAULT_PRODUCTS),
        "receptions": list(DEFAULT_MOUVEMENTS),
        "prise_appel": list(DEFAULT_PRISE_APPEL),
        "reseau": list(DEFAULT_RESEAUX),
        "feedback": list(DEFAULT_FEEDBACK),
        "points_de_vente": list(DEFAULT_POINTS_DE_VENTE),
        "_reference_rows": [],
    }


def lire_references():
    refs = _references_par_defaut()
    type_map = {
        "CAMPAGNE": "campagnes",
        "TO": "to",
        "PRODUIT": "produits",
        "RECEPTION": "receptions",
        "PRISE_APPEL": "prise_appel",
        "RESEAU": "reseau",
        "FEEDBACK": "feedback",
        "POINT_DE_VENTE": "points_de_vente",
    }
    try:
        rows = _charger_references_cache(False)
        refs["_reference_rows"] = rows
        for reference_type, target in type_map.items():
            values = values_for_type(rows, reference_type)
            if values:
                refs[target] = values
        return refs
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.warning(f"Références de la base indisponibles : {exc}")
        return refs


def _empreinte_appel(nouvel_appel):
    payload = json.dumps(nouvel_appel, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sauvegarder_appel(nouvel_appel):
    """Enregistre, puis confirme avant d'afficher un succès."""
    fingerprint = _empreinte_appel(nouvel_appel)
    last_fingerprint = st.session_state.get("last_call_fingerprint")
    last_time = float(st.session_state.get("last_call_saved_at", 0))
    if fingerprint == last_fingerprint and time.time() - last_time < 90:
        st.warning("Cet appel vient déjà d'être enregistré. Aucun doublon n'a été créé.")
        return False

    try:
        created = get_database_service().create_call(nouvel_appel)
        if not created.get("id"):
            raise DatabaseError("La base n'a pas confirmé l'identifiant de l'appel.")
        st.session_state["last_call_fingerprint"] = fingerprint
        st.session_state["last_call_saved_at"] = time.time()
        invalider_cache_donnees()
        return True
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"L'appel n'a pas été enregistré : {exc}")
        st.info("Vos informations restent dans le formulaire. Réessayez après vérification.")
        return False


def ajouter_to(nouveau_to):
    try:
        result = get_database_service().add_reference("TO", nouveau_to)
        invalider_cache_donnees()
        return result
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"Ajout impossible : {exc}")
        return False


def desactiver_to(item_id, etag=None):
    try:
        get_database_service().deactivate_reference(item_id, etag=etag)
        invalider_cache_donnees()
        return True
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"Désactivation impossible : {exc}")
        return False


def supprimer_appel(item_id, etag=None):
    if not item_id:
        return False
    try:
        get_database_service().delete_call(str(item_id), etag=etag)
        invalider_cache_donnees()
        return True
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"Suppression impossible : {exc}")
        return False


def modifier_appel(item_id, valeurs, etag=None):
    if not item_id:
        return False
    try:
        get_database_service().update_call(str(item_id), valeurs, etag=etag)
        invalider_cache_donnees()
        return True
    except (DatabaseConfigurationError, DatabaseError) as exc:
        st.error(f"Modification impossible : {exc}")
        return False


def _texte_formulaire(value):
    try:
        if value is None or pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def _options_avec_valeur(options, current, *, blank=False):
    result = [""] if blank else []
    for value in list(options or []):
        text = _texte_formulaire(value).strip()
        if text and text.casefold() not in {item.casefold() for item in result}:
            result.append(text)
    current_text = _texte_formulaire(current).strip()
    if current_text and current_text.casefold() not in {
        item.casefold() for item in result
    }:
        result.append(current_text)
    return result or ([""] if blank else [current_text or "Non renseigné"])


def _heure_formulaire(value):
    text = _texte_formulaire(value).strip()
    try:
        return datetime.strptime(text[:5], "%H:%M").time()
    except (TypeError, ValueError):
        return datetime.now().replace(second=0, microsecond=0).time()


# ============================================================================
# PAGE : SAISIE D'APPEL
# ============================================================================


def page_saisie(refs):
    st.markdown("## Saisie d'appel")
    st.caption("Formulaire adapte a la campagne selectionnee")

    if "campagne_sel" not in st.session_state:
        st.session_state["campagne_sel"] = None

    campagne_sel = st.session_state["campagne_sel"]

    # ------------------------------------------------------------------
    # ÉTAPE 1 : Sélection de la campagne (chips sans emoji)
    # ------------------------------------------------------------------
    if not campagne_sel:
        st.markdown("### Choisissez la campagne")
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        camps = [(str(value), str(value)) for value in refs["campagnes"]]

        cols = st.columns(len(camps))
        for i, (label, value) in enumerate(camps):
            with cols[i]:
                if st.button(label, key=f"chip_{value}", use_container_width=True):
                    st.session_state["campagne_sel"] = value
                    st.rerun()

        return

    # ------------------------------------------------------------------
    # ÉTAPE 2 : Formulaire adapté
    # ------------------------------------------------------------------
    col1, col2 = st.columns([3, 1], gap="medium")

    with col1:
        with st.form("form_appel", clear_on_submit=False):
            # Bloc 1 : Informations générales
            st.markdown(f"#### Informations generales — <span style='color:{NSIA['gold']}'>{campagne_sel}</span>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                date_appel = st.date_input("Date", value=date.today())
                heure_appel = st.time_input("Heure", value=datetime.now().time())
                to_appel = st.selectbox("TO (Teleconseiller) *", options=refs["to"])
                nom_client = st.text_input("Nom du Client", placeholder="Ex: Koffi Ama")
            with c2:
                telephone = st.text_input("Numero de telephone", placeholder="Ex: 90 00 00 00")
                reception = st.selectbox("Reception / Mouvt *", options=refs["receptions"])
                point_vente = st.selectbox("Point de vente", options=[""] + refs["points_de_vente"])

            # Bloc 2 : Détails contrat / produit
            st.markdown("#### Details contrat / produit")
            if campagne_sel in ["ONBOARDING", "SATURATION"]:
                c3, c4 = st.columns(2)
                with c3:
                    immatriculation = st.text_input("Immatriculation", placeholder="Ex: TG 1234 AB")
                    police = st.text_input("Police / N contrat", placeholder="Ex: POL-2024-001")
                    produit_existant = st.selectbox("Produit existant", options=[""] + refs["produits"])
                with c4:
                    produit_propose = st.selectbox("Produit propose", options=[""] + refs["produits"])
                    prise_appel = st.selectbox("Prise d'appel", options=refs["prise_appel"])
            elif campagne_sel == "RECEPTION":
                c3, c4 = st.columns(2)
                with c3:
                    immatriculation = st.text_input("Immatriculation", placeholder="Ex: TG 1234 AB")
                    police = st.text_input("Police / N contrat", placeholder="Ex: POL-2024-001")
                with c4:
                    produit_souhaite = st.selectbox("Produit souhaite", options=[""] + refs["produits"])
                    prise_appel = st.selectbox("Prise d'appel", options=refs["prise_appel"])
                produit_existant = ""
                produit_propose = ""
            else:
                c3, c4 = st.columns(2)
                with c3:
                    immatriculation = st.text_input("Immatriculation", placeholder="Ex: TG 1234 AB")
                    police = st.text_input("Police / N contrat", placeholder="Ex: POL-2024-001")
                with c4:
                    prise_appel = st.selectbox("Prise d'appel", options=refs["prise_appel"])
                produit_existant = ""
                produit_propose = ""
                produit_souhaite = ""

            # Bloc 3 : Résultat et suivi
            st.markdown("#### Resultat et suivi")
            c5, c6 = st.columns(2)
            with c5:
                if campagne_sel == "ONBOARDING":
                    satisfaction = st.selectbox("Satisfaction", options=["", "Non satisfait", "Satisfait", "Neutre"])
                    recommendation = st.selectbox("Recommendation", options=["Neutre"] + [str(i) for i in range(1, 11)])
                    feedback = st.selectbox("Feedback", options=[""] + refs["feedback"])
                elif campagne_sel == "SATURATION":
                    feedback = st.selectbox("Feedback", options=[""] + refs["feedback"])
                    satisfaction = ""
                    recommendation = ""
                elif campagne_sel == "RECEPTION":
                    feedback = ""
                    satisfaction = ""
                    recommendation = ""
                else:
                    feedback = st.selectbox("Feedback", options=[""] + refs["feedback"])
                    satisfaction = ""
                    recommendation = ""

            with c6:
                ca = st.number_input("Chiffre d'affaires (FCFA)", min_value=0, value=0, step=1000)
                commentaire = st.text_area("Commentaire", placeholder="Notes supplementaires...", height=100)

            statut = ""

            submitted = st.form_submit_button("Enregistrer l'appel", type="primary", use_container_width=True)

            if submitted:
                nom_client_safe = nom_client.strip() if isinstance(nom_client, str) else nom_client
                telephone_safe = telephone.strip() if isinstance(telephone, str) else telephone
                nom_affiche = nom_client_safe or "Appel sans nom"
                nouvel_appel = {
                    "Date": date_appel,
                    "TO": to_appel,
                    "Nom du Client": nom_client_safe or None,
                    "telephone": telephone_safe or None,
                    "Immatriculation": immatriculation or None,
                    "Police": police or None,
                    "Campagne": campagne_sel,
                    "Reception": reception,
                    "Prise d'appel": prise_appel,
                    "Produit existant": produit_existant or None,
                    "Produit proposé": produit_propose or None,
                    "Produit souhaite": produit_souhaite if campagne_sel == "RECEPTION" else None,
                    "Feedback": feedback or None,
                    "CA": ca,
                    "Point de vente": point_vente or None,
                    "Heure_appel": heure_appel.strftime("%H:%M"),
                    "Statut": statut or None,
                    "Motif_non_reponse": None,
                    "Commentaire": commentaire or None,
                    "Satisfaction": satisfaction or None,
                    "Recommendation": recommendation or None,
                }

                if sauvegarder_appel(nouvel_appel):
                    st.success(f"Appel enregistre pour {nom_affiche} !")
                    st.balloons()
                    st.session_state["campagne_sel"] = None
                    st.rerun()

    with col2:
        st.markdown("### Campagne active")
        st.info(campagne_sel)

        if st.button("Changer de campagne", type="secondary", use_container_width=True):
            st.session_state["campagne_sel"] = None
            st.rerun()

        st.markdown("---")
        st.markdown("#### Guide de saisie")
        st.markdown(
            f"""
<div style="background-color:rgba(32,44,84,0.35);padding:1rem;border-radius:0.75rem;border-left:3px solid {NSIA['gold']};color:{NSIA['silver']};">
<ul style="margin:0;padding-left:1.1rem;">
<li><strong>Champs recommandes :</strong> Nom, Telephone</li>
<li>Enregistrement possible <strong>sans nom ni telephone</strong></li>
<li>Le formulaire s'adapte a la campagne choisie</li>
</ul>
</div>
""",
            unsafe_allow_html=True,
        )


# ============================================================================
# PAGE : TABLEAU DE BORD
# ============================================================================


def calculer_kpis(df):
    if df.empty:
        return {
            "nb_appels": 0,
            "nb_repondus": 0,
            "nb_non_repondus": 0,
            "taux_reponse": 0.0,
            "ca_total": 0,
            "ca_moyen": 0.0,
            "top_to": "N/A",
            "top_campagne": "N/A",
            "top_produit": "N/A",
        }

    nb_total = len(df)
    nb_repondus = len(df[df["Prise d'appel"] == "Oui"]) if "Prise d'appel" in df.columns else 0
    nb_non_repondus = nb_total - nb_repondus
    taux_reponse = (nb_repondus / nb_total * 100) if nb_total > 0 else 0.0
    ca_total = df["CA"].sum() if "CA" in df.columns else 0
    ca_moyen = ca_total / nb_total if nb_total > 0 else 0.0

    top_to = "N/A"
    if "TO" in df.columns and ca_total > 0:
        try:
            top_to = df.groupby("TO")["CA"].sum().idxmax()
        except ValueError:
            pass

    top_campagne = "N/A"
    if "Campagne" in df.columns and not df["Campagne"].dropna().empty:
        try:
            top_campagne = df["Campagne"].value_counts().idxmax()
        except ValueError:
            pass

    top_produit = "N/A"
    if "Produit proposé" in df.columns and ca_total > 0:
        try:
            produits_ca = df.groupby("Produit proposé")["CA"].sum()
            if not produits_ca.empty:
                top_produit = produits_ca.idxmax()
        except ValueError:
            pass

    return {
        "nb_appels": nb_total,
        "nb_repondus": nb_repondus,
        "nb_non_repondus": nb_non_repondus,
        "taux_reponse": round(taux_reponse, 1),
        "ca_total": ca_total,
        "ca_moyen": round(ca_moyen, 0),
        "top_to": top_to,
        "top_campagne": top_campagne,
        "top_produit": top_produit,
    }


def page_tableau_bord(df):
    st.header("Tableau de bord")

    if df.empty:
        st.warning("Aucune donnee disponible. Commencez par saisir des appels.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        filtre_date_debut = st.date_input("Date debut", value=None)
    with c2:
        filtre_date_fin = st.date_input("Date fin", value=None)
    with c3:
        filtre_to = st.multiselect("TO", options=sorted(df["TO"].dropna().unique()))
    with c4:
        filtre_campagne = st.multiselect("Campagne", options=sorted(df["Campagne"].dropna().unique()))

    with st.expander("Autres filtres", expanded=False):
        c5, c6 = st.columns(2)
        with c5:
            filtre_reception = st.multiselect("Reception", options=sorted(df["Reception"].dropna().unique()))
        with c6:
            filtre_produit = st.multiselect("Produit propose", options=sorted(df.get("Produit proposé", pd.Series()).dropna().unique()))

    df_filtre = df.copy()
    if filtre_date_debut:
        df_filtre = df_filtre[df_filtre["Date"] >= filtre_date_debut]
    if filtre_date_fin:
        df_filtre = df_filtre[df_filtre["Date"] <= filtre_date_fin]
    if filtre_to:
        df_filtre = df_filtre[df_filtre["TO"].isin(filtre_to)]
    if filtre_campagne:
        df_filtre = df_filtre[df_filtre["Campagne"].isin(filtre_campagne)]
    if filtre_reception:
        df_filtre = df_filtre[df_filtre["Reception"].isin(filtre_reception)]
    if filtre_produit and "Produit proposé" in df_filtre.columns:
        df_filtre = df_filtre[df_filtre["Produit proposé"].isin(filtre_produit)]

    if df_filtre.empty:
        st.warning("Aucune donnee correspondant aux filtres selectionnes.")
        return

    kpis = calculer_kpis(df_filtre)

    st.markdown("### Indicateurs cles")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Nb Appels", kpis["nb_appels"])
    c2.metric("Repondus", kpis["nb_repondus"])
    c3.metric("Non Repondus", kpis["nb_non_repondus"])
    c4.metric("Taux Reponse", f"{kpis['taux_reponse']}%")
    c5.metric("CA Total (FCFA)", f"{kpis['ca_total']:,.0f}".replace(",", " "))

    c6, c7, c8 = st.columns(3)
    c6.metric("CA Moyen / Appel (FCFA)", f"{kpis['ca_moyen']:,.0f}".replace(",", " "))
    c7.metric("Top TO", kpis["top_to"])
    c8.metric("Top Campagne", kpis["top_campagne"])

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Campagnes & Produits", "Performance TO", "CA & Appels", "Details"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            camp_counts = df_filtre["Campagne"].value_counts().reset_index()
            camp_counts.columns = ["Campagne", "Nb Appels"]
            fig_camp = px.bar(camp_counts, x="Campagne", y="Nb Appels", color="Nb Appels", title="Nombre d'appels par campagne", text="Nb Appels")
            fig_camp.update_layout(showlegend=False)
            st.plotly_chart(fig_camp, use_container_width=True)
        with c2:
            camp_ca = df_filtre.groupby("Campagne")["CA"].sum().reset_index()
            camp_ca.columns = ["Campagne", "CA (FCFA)"]
            fig_ca = px.bar(camp_ca, x="Campagne", y="CA (FCFA)", color="CA (FCFA)", title="Chiffre d'affaires par campagne (FCFA)", text="CA (FCFA)")
            fig_ca.update_layout(showlegend=False)
            st.plotly_chart(fig_ca, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            prod_counts = df_filtre.get("Produit proposé", pd.Series()).value_counts().reset_index()
            prod_counts.columns = ["Produit", "Nb Appels"]
            fig_prod = px.pie(prod_counts, values="Nb Appels", names="Produit", title="Repartition des appels par produit propose")
            st.plotly_chart(fig_prod, use_container_width=True)
        with c4:
            prod_ca = df_filtre.groupby("Produit proposé")["CA"].sum().reset_index()
            prod_ca.columns = ["Produit", "CA (FCFA)"]
            fig_prod_ca = px.bar(prod_ca, x="Produit", y="CA (FCFA)", color="CA (FCFA)", title="CA par produit propose (FCFA)", text="CA (FCFA)")
            fig_prod_ca.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_prod_ca, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            to_counts = df_filtre["TO"].value_counts().reset_index()
            to_counts.columns = ["TO", "Nb Appels"]
            fig_to_count = px.bar(to_counts, x="TO", y="Nb Appels", color="Nb Appels", title="Nb appels par TO", text="Nb Appels")
            fig_to_count.update_layout(showlegend=False)
            st.plotly_chart(fig_to_count, use_container_width=True)
        with c2:
            to_ca = df_filtre.groupby("TO")["CA"].sum().reset_index()
            to_ca.columns = ["TO", "CA (FCFA)"]
            fig_to_ca = px.bar(to_ca, x="TO", y="CA (FCFA)", color="CA (FCFA)", title="CA par TO (FCFA)", text="CA (FCFA)")
            fig_to_ca.update_layout(showlegend=False)
            st.plotly_chart(fig_to_ca, use_container_width=True)

        to_stats = (
            df_filtre.groupby("TO")["Prise d'appel"]
            .apply(lambda x: (x == "Oui").sum() / len(x) * 100 if len(x) > 0 else 0)
            .reset_index()
        )
        to_stats.columns = ["TO", "Taux Reponse (%)"]
        fig_to_taux = px.bar(to_stats, x="TO", y="Taux Reponse (%)", color="Taux Reponse (%)", title="Taux de reponse par TO (%)", text="Taux Reponse (%)")
        fig_to_taux.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig_to_taux, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            if "Date" in df_filtre.columns:
                df_daily = df_filtre.groupby("Date")["CA"].sum().reset_index().sort_values("Date")
                df_daily["CA Cumule"] = df_daily["CA"].cumsum()
                fig_ca_cum = px.line(df_daily, x="Date", y="CA Cumule", title="CA cumule dans le temps (FCFA)", markers=True)
                st.plotly_chart(fig_ca_cum, use_container_width=True)
        with c2:
            if "Date" in df_filtre.columns:
                daily_counts = df_filtre.groupby("Date").size().reset_index(name="Nb Appels").sort_values("Date")
                fig_daily = px.bar(daily_counts, x="Date", y="Nb Appels", title="Volume d'appels par jour", text="Nb Appels")
                fig_daily.update_layout(showlegend=False)
                st.plotly_chart(fig_daily, use_container_width=True)

        rec_stats = df_filtre.groupby("Reception").agg(Nb_Appels=("Reception", "size"), CA=("CA", "sum")).reset_index()
        rec_stats.columns = ["Reception", "Nb Appels", "CA (FCFA)"]
        c3, c4 = st.columns(2)
        with c3:
            fig_rec_count = px.pie(rec_stats, values="Nb Appels", names="Reception", title="Repartition REN vs AFN (nb appels)")
            st.plotly_chart(fig_rec_count, use_container_width=True)
        with c4:
            fig_rec_ca = px.pie(rec_stats, values="CA (FCFA)", names="Reception", title="Repartition REN vs AFN (CA FCFA)")
            st.plotly_chart(fig_rec_ca, use_container_width=True)

    with tab4:
        st.subheader("Statut des appels")
        status_counts = df_filtre["Statut"].value_counts().reset_index()
        status_counts.columns = ["Statut", "Nombre"]
        fig_status = px.bar(status_counts, x="Statut", y="Nombre", color="Nombre", title="Repartition par statut d'appel", text="Nombre")
        fig_status.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_status, use_container_width=True)

        st.subheader("Feedbacks clients")
        fb_counts = df_filtre.get("Feedback", pd.Series()).dropna().value_counts().reset_index()
        fb_counts.columns = ["Feedback", "Nombre"]
        if not fb_counts.empty:
            fig_fb = px.bar(fb_counts, x="Feedback", y="Nombre", color="Nombre", title="Repartition des feedbacks", text="Nombre")
            fig_fb.update_layout(showlegend=False, xaxis_tickangle=-30)
            st.plotly_chart(fig_fb, use_container_width=True)
        else:
            st.info("Aucun feedback enregistre.")


# ============================================================================
# PAGE : HISTORIQUE
# ============================================================================


def _formulaire_modification_appel(selected_row, refs):
    """Affiche l'éditeur d'un appel sélectionné sans exposer son identifiant."""
    item_id = _texte_formulaire(selected_row.get("_item_id")).strip()
    if not item_id:
        return

    with st.expander("Modifier l'appel sélectionné", expanded=False):
        with st.form(f"modifier_appel_{item_id}"):
            def select_current(label, options, field, *, blank=False):
                current = _texte_formulaire(selected_row.get(field)).strip()
                choices = _options_avec_valeur(options, current, blank=blank)
                return st.selectbox(
                    label,
                    choices,
                    index=choices.index(current) if current in choices else 0,
                )

            current_date = selected_row.get("Date")
            if isinstance(current_date, pd.Timestamp):
                current_date = current_date.date()
            if not isinstance(current_date, date):
                current_date = date.today()

            c1, c2 = st.columns(2)
            with c1:
                edit_date = st.date_input("Date", value=current_date)
                edit_heure = st.time_input(
                    "Heure", value=_heure_formulaire(selected_row.get("Heure_appel"))
                )
                edit_to = select_current("TO *", refs["to"], "TO")
                edit_nom = st.text_input(
                    "Nom du Client",
                    value=_texte_formulaire(selected_row.get("Nom du Client")),
                )
                edit_telephone = st.text_input(
                    "Numéro de téléphone",
                    value=_texte_formulaire(selected_row.get("telephone")),
                )
                edit_campagne = select_current(
                    "Campagne *", refs["campagnes"], "Campagne"
                )
                edit_reception = select_current(
                    "Réception *", refs["receptions"], "Reception"
                )
                edit_prise = select_current(
                    "Prise d'appel", refs["prise_appel"], "Prise d'appel"
                )

            with c2:
                edit_immatriculation = st.text_input(
                    "Immatriculation",
                    value=_texte_formulaire(selected_row.get("Immatriculation")),
                )
                edit_police = st.text_input(
                    "Police", value=_texte_formulaire(selected_row.get("Police"))
                )
                edit_existing = select_current(
                    "Produit existant",
                    refs["produits"],
                    "Produit existant",
                    blank=True,
                )
                edit_proposed = select_current(
                    "Produit proposé",
                    refs["produits"],
                    "Produit proposé",
                    blank=True,
                )
                edit_wanted = select_current(
                    "Produit souhaité",
                    refs["produits"],
                    "Produit souhaite",
                    blank=True,
                )
                edit_point = select_current(
                    "Point de vente",
                    refs["points_de_vente"],
                    "Point de vente",
                    blank=True,
                )
                edit_status = select_current(
                    "Statut", DEFAULT_STATUS, "Statut", blank=True
                )
                edit_motif = select_current(
                    "Motif de non-réponse",
                    DEFAULT_MOTIFS,
                    "Motif_non_reponse",
                    blank=True,
                )

            c3, c4 = st.columns(2)
            with c3:
                edit_satisfaction = select_current(
                    "Satisfaction",
                    ["Non satisfait", "Satisfait", "Neutre"],
                    "Satisfaction",
                    blank=True,
                )
                edit_recommendation = select_current(
                    "Recommandation",
                    ["Neutre"] + [str(i) for i in range(1, 11)],
                    "Recommendation",
                    blank=True,
                )
            with c4:
                edit_feedback = select_current(
                    "Feedback", refs["feedback"], "Feedback", blank=True
                )
                current_ca = pd.to_numeric(
                    pd.Series([selected_row.get("CA")]), errors="coerce"
                ).fillna(0).iloc[0]
                edit_ca = st.number_input(
                    "Chiffre d'affaires (FCFA)",
                    min_value=0,
                    value=int(current_ca),
                    step=1000,
                )

            edit_comment = st.text_area(
                "Commentaire",
                value=_texte_formulaire(selected_row.get("Commentaire")),
            )
            save_edit = st.form_submit_button(
                "Enregistrer les modifications",
                type="primary",
                use_container_width=True,
            )

            if save_edit:
                if not edit_to or not edit_campagne or not edit_reception:
                    st.error("Le TO, la campagne et la réception sont obligatoires.")
                    return
                changes = {
                    "Date": edit_date,
                    "TO": edit_to,
                    "Nom du Client": edit_nom.strip() or None,
                    "telephone": edit_telephone.strip() or None,
                    "Immatriculation": edit_immatriculation.strip() or None,
                    "Police": edit_police.strip() or None,
                    "Campagne": edit_campagne,
                    "Reception": edit_reception,
                    "Prise d'appel": edit_prise or None,
                    "Produit existant": edit_existing or None,
                    "Produit proposé": edit_proposed or None,
                    "Produit souhaite": edit_wanted or None,
                    "Point de vente": edit_point or None,
                    "Heure_appel": edit_heure.strftime("%H:%M"),
                    "Statut": edit_status or None,
                    "Motif_non_reponse": edit_motif or None,
                    "Satisfaction": edit_satisfaction or None,
                    "Recommendation": edit_recommendation or None,
                    "Feedback": edit_feedback or None,
                    "Commentaire": edit_comment.strip() or None,
                    "CA": edit_ca,
                }
                if modifier_appel(
                    item_id, changes, selected_row.get("_etag")
                ):
                    st.success("L'appel a été modifié dans la base.")
                    st.rerun()


def page_historique(df, refs):
    st.header("Historique des appels")

    if df.empty:
        st.warning("Aucune donnee disponible.")
        return

    periode_type = st.selectbox(
        "Periode",
        options=["Jour", "Semaine", "Mois", "Annee"],
        index=0,
        key="hist_periode",
    )

    with st.form("form_historique", clear_on_submit=False):
        df_recherche = df.copy()
        if "Date" not in df_recherche.columns:
            df_recherche["Date"] = pd.to_datetime(df_recherche["Date"], errors="coerce").dt.date

        filtre_immat = ""
        filtre_police = ""
        filtre_nom = ""

        if periode_type == "Jour":
            jour = st.date_input("Jour", value=None, key="hist_jour")
            if jour:
                df_recherche = df_recherche[df_recherche["Date"] == jour]
        elif periode_type == "Semaine":
            c1, c2 = st.columns(2)
            with c1:
                annee_sem = st.number_input("Annee", min_value=2020, max_value=2100, value=2026, step=1, key="hist_sem_annee")
            with c2:
                semaine = st.number_input("Semaine", min_value=1, max_value=53, value=1, step=1, key="hist_sem_num")
            if annee_sem and semaine:
                df_recherche = df_recherche[
                    df_recherche["Date"].apply(lambda d: _is_same_iso_week(d, annee_sem, semaine) if pd.notna(d) else False)
                ]
        elif periode_type == "Mois":
            c1, c2 = st.columns(2)
            with c1:
                annee_mois = st.number_input("Annee", min_value=2020, max_value=2100, value=2026, step=1, key="hist_mois_annee")
            with c2:
                mois = st.selectbox("Mois", options=list(range(1, 13)), index=0, key="hist_mois_num")
            if annee_mois and mois:
                df_recherche = df_recherche[
                    df_recherche["Date"].apply(lambda d: _is_same_year_month(d, annee_mois, mois) if pd.notna(d) else False)
                ]
        elif periode_type == "Annee":
            annee = st.number_input("Annee", min_value=2020, max_value=2100, value=2026, step=1, key="hist_annee")
            if annee:
                df_recherche = df_recherche[
                    df_recherche["Date"].apply(lambda d: _is_same_year(d, annee) if pd.notna(d) else False)
                ]

        c1, c2, c3 = st.columns(3)
        with c1:
            filtre_immat = st.text_input("Immatriculation", placeholder="Ex: TG 1234 AB", key="hist_immat")
        with c2:
            filtre_police = st.text_input("Police", placeholder="Ex: POL-2024-001", key="hist_police")
        with c3:
            filtre_nom = st.text_input("Nom du client", placeholder="Ex: Koffi", key="hist_nom")

        submitted = st.form_submit_button("Rechercher", type="primary", use_container_width=True)
        reset = st.form_submit_button("Reinitialiser", type="secondary", use_container_width=True)

    if reset:
        st.rerun()

    if submitted:
        if filtre_immat:
            rech = filtre_immat.lower()
            df_recherche = df_recherche[df_recherche.get("Immatriculation", pd.Series()).str.lower().str.contains(rech, na=False)]
        if filtre_police:
            rech = filtre_police.lower()
            df_recherche = df_recherche[df_recherche.get("Police", pd.Series()).str.lower().str.contains(rech, na=False)]
        if filtre_nom:
            rech = filtre_nom.lower()
            df_recherche = df_recherche[df_recherche["Nom du Client"].str.lower().str.contains(rech, na=False)]

    cols_affichage = [
        "Date",
        "Heure_appel",
        "TO",
        "Nom du Client",
        "telephone",
        "Police",
        "Immatriculation",
        "Campagne",
        "Reception",
        "Prise d'appel",
        "Produit existant",
        "Produit proposé",
        "CA",
        "Statut",
        "Feedback",
        "Satisfaction",
        "Recommendation",
        "Point de vente",
    ]
    cols_dispo = [c for c in cols_affichage if c in df_recherche.columns]
    df_aff = df_recherche[cols_dispo].copy()
    df_aff["_item_id"] = df_recherche["_item_id"]
    df_aff["_etag"] = df_recherche["_etag"]

    if "Date" in df_aff.columns and "Heure_appel" in df_aff.columns:
        df_aff = df_aff.sort_values(by=["Date", "Heure_appel"], ascending=[False, False])

    selection = st.dataframe(
        df_aff,
        use_container_width=True,
        height=500,
        column_config={"_item_id": None, "_etag": None},
        selection_mode="multi-row",
        on_select="rerun",
        key="hist_selection",
    )
    selected_rows = selection.get("selection", {}).get("rows", []) or []
    if selected_rows:
        st.caption(f"Ligne(s) selectionnee(s): {len(selected_rows)}")
        if len(selected_rows) == 1 and selected_rows[0] < len(df_aff):
            selected_item_id = _texte_formulaire(
                df_aff.iloc[selected_rows[0]].get("_item_id")
            ).strip()
            source_rows = df_recherche[
                df_recherche["_item_id"].astype(str) == selected_item_id
            ]
            selected_row = (
                source_rows.iloc[0]
                if not source_rows.empty
                else df_aff.iloc[selected_rows[0]]
            )
            _formulaire_modification_appel(selected_row, refs)

        confirmation = st.checkbox(
            "Je confirme la suppression définitive des appels sélectionnés.",
            key="confirmation_suppression_historique",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "Supprimer la selection",
                type="secondary",
                use_container_width=True,
                key="supprimer_historique",
                disabled=not confirmation,
            ):
                try:
                    items = []
                    for i in selected_rows:
                        if i < len(df_aff):
                            row = df_aff.iloc[i]
                            item_id = row.get("_item_id")
                            if item_id:
                                items.append((str(item_id), row.get("_etag")))
                    if not items:
                        st.error("Aucune ligne valide selectionnee.")
                    else:
                        success_count = 0
                        for item_id, etag in items:
                            if supprimer_appel(item_id, etag):
                                success_count += 1
                        if success_count:
                            st.success(f"{success_count} ligne(s) supprimee(s).")
                            st.rerun()
                        else:
                            st.error("Aucune suppression n'a été confirmée par la base.")
                except Exception:
                    st.error(
                        "Une erreur inattendue a empêché la suppression. "
                        "Actualisez les données puis réessayez."
                    )
        with c2:
            if st.button("Rafraichir", type="primary", use_container_width=True, key="refresh_historique"):
                st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        csv = df_aff.drop(columns=["_item_id", "_etag"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("Exporter en CSV", data=csv, file_name=f"appels_export_{date.today().isoformat()}.csv", mime="text/csv")
    with c2:
        output = io.BytesIO()
        workbook = pd.ExcelWriter(output, engine="xlsxwriter")
        df_export = df_aff.drop(columns=["_item_id", "_etag"], errors="ignore")
        df_export.to_excel(workbook, sheet_name="Call", index=False)
        worksheet = workbook.sheets["Call"]
        worksheet.autofilter(0, 0, df_export.shape[0], df_export.shape[1] - 1)
        worksheet.freeze_panes(1, 0)
        header_fmt = workbook.book.add_format(
            {"bold": True, "bg_color": "#D9E1F2", "border": 1, "align": "center", "valign": "vcenter"}
        )
        for col_num, value in enumerate(df_export.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, max(12, min(40, len(str(value)) + 2)))
        workbook.close()
        st.download_button("Exporter en Excel", data=output.getvalue(), file_name=f"appels_export_{date.today().isoformat()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================================
# PAGE : REFERENCES
# ============================================================================


def page_references(refs):
    st.header("Gestion des references")

    st.info("Visualisez et modifiez les listes de reference utilisees dans les formulaires.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Campagnes")
        for c in refs["campagnes"]:
            st.write(f"- {c}")
        st.subheader("TOs")
        for t in refs["to"]:
            st.write(f"- {t}")
    with c2:
        st.subheader("Receptions")
        for r in refs["receptions"]:
            st.write(f"- {r}")
        st.subheader("Prise d'appel")
        for p in refs["prise_appel"]:
            st.write(f"- {p}")
    with c3:
        st.subheader("Produits")
        for p in refs["produits"]:
            st.write(f"- {p}")
        st.subheader("Statuts")
        for s in DEFAULT_STATUS:
            st.write(f"- {s}")


# ============================================================================
# PAGE : OPERATEURS
# ============================================================================


def page_operateurs(refs):
    st.header("Gestion des operateurs / TOs")

    st.markdown(
        "Ajoutez ou désactivez des téléconseillers. Les modifications sont "
        "enregistrées immédiatement dans la base en ligne."
    )

    st.subheader("Operateurs existants")
    to_list = refs["to"]

    if not to_list:
        st.warning("Aucun operateur enregistre.")
    else:
        rows_by_name = {
            str(row.get("Valeur") or "").strip().casefold(): row
            for row in refs.get("_reference_rows", [])
            if str(row.get("TypeReference") or "").strip().upper() == "TO"
        }
        for to in to_list:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**{to}**")
            with c2:
                reference_row = rows_by_name.get(str(to).strip().casefold())
                if st.button(
                    "Désactiver",
                    key=f"del_{to}",
                    disabled=reference_row is None,
                    help=(
                        None
                        if reference_row is not None
                        else "Cette valeur par défaut doit d'abord être créée dans la base."
                    ),
                ):
                    result = desactiver_to(
                        reference_row.get("_item_id"), reference_row.get("_etag")
                    )
                    if result:
                        st.success(f"Opérateur {to} désactivé.")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la désactivation.")

    st.markdown("---")
    st.subheader("Ajouter un operateur")

    with st.form("form_ajout_to"):
        nouveau_to = st.text_input("Nom du nouvel operateur / TO", placeholder="Ex: Jean, Marie, Kofi...")
        submitted = st.form_submit_button("Ajouter l'operateur", type="primary", use_container_width=True)

        if submitted:
            if not nouveau_to or not str(nouveau_to).strip():
                st.error("Veuillez saisir un nom d'operateur.")
            else:
                result = ajouter_to(nouveau_to)
                if result in {"ajoute", "reactive"}:
                    st.success(f"Operateur '{nouveau_to}' ajoute avec succes !")
                    st.rerun()
                elif result == "existe":
                    st.warning(f"L'operateur '{nouveau_to}' existe deja dans la base.")
                else:
                    st.error("Erreur lors de l'ajout.")


# ============================================================================
# PAGE : PARAMÈTRES
# ============================================================================


def page_parametres():
    st.header("Parametres")

    st.markdown("### Source de données")
    st.code(DATA_SOURCE_LABEL, language="text")

    if st.button("Tester la connexion à la base", type="primary"):
        try:
            get_database_service().healthcheck()
            st.success("Connexion aux deux tables Supabase confirmée.")
        except (DatabaseConfigurationError, DatabaseError) as exc:
            st.error(f"Connexion non disponible : {exc}")

    st.markdown("### Palette NSIA")
    for k, v in NSIA.items():
        st.markdown(f"- **{k}**: `{v}`")

    st.markdown("### Informations")
    st.markdown(f"- Page: **NSIA Call Center**")
    st.markdown(f"- Layout: **wide**")


# ============================================================================
# NAVIGATION PRINCIPALE
# ============================================================================


def main():
    utilisateur = authentifier_utilisateur()

    st.sidebar.title("NSIA Call Center")
    st.sidebar.markdown("**Assurances Togo**")
    st.sidebar.caption(utilisateur.get("name") or utilisateur.get("email"))
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Saisie d'appel",
            "Tableau de bord",
            "Historique",
            "Operateurs",
            "References",
            "Parametres",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"Source : `Base en ligne`\nDernière actualisation : "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    if _secret_section("application").get("access_required", True):
        if st.sidebar.button("Verrouiller l'application", use_container_width=True):
            st.session_state["access_granted"] = False
            st.rerun()

    df = lire_appels_base()
    refs = lire_references()

    if page == "Saisie d'appel":
        page_saisie(refs)
    elif page == "Tableau de bord":
        page_tableau_bord(df)
    elif page == "Historique":
        page_historique(df, refs)
    elif page == "Operateurs":
        page_operateurs(refs)
    elif page == "References":
        page_references(refs)
    elif page == "Parametres":
        page_parametres()


if __name__ == "__main__":
    main()
