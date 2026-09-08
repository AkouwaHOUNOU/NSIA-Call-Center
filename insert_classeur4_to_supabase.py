# -*- coding: utf-8 -*-
"""Insertion des données du fichier Classeur4.xlsx vers la table historique Supabase."""
from __future__ import annotations

import os
from datetime import datetime
import pandas as pd
from database_service import DatabaseConfig, DatabaseService, DatabaseError

EXCEL_PATH = r"C:\Users\houno\Downloads\Classeur4.xlsx"
SECRETS_PATH = os.path.join(
    os.path.dirname(__file__), ".streamlit", "secrets.toml"
)


def _load_secrets(path: str) -> dict:
    import tomllib

    with open(path, "rb") as f:
        return tomllib.load(f)


def _safe_text(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return str(value).strip() or None


def insert_classeur4_to_supabase():
    secrets = _load_secrets(SECRETS_PATH)
    database_cfg = DatabaseConfig.from_mapping(secrets.get("database", {}))
    service = DatabaseService(database_cfg)

    df = pd.read_excel(EXCEL_PATH, sheet_name="Feuil1")
    df.columns = [str(col).strip() for col in df.columns]

    expected_columns = {
        "Produit existant": "Produit existant",
        "Nom Souscripteur": "Nom du Client",
        "Telephone": "telephone",
        "Numero Immatriculation": "Immatriculation",
        "Numero de police": "Police",
        "Feedback": "Feedback",
        "date": "Date",
        "CAMPAGNE": "Campagne",
    }
    df = df.rename(columns=expected_columns)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["CA"] = 0

    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        values = {
            "Date": row.get("Date").date().isoformat() if pd.notna(row.get("Date")) else None,
            "TO": _safe_text(row.get("TO")) or "Inconnu",
            "Nom du Client": _safe_text(row.get("Nom du Client")),
            "telephone": _safe_text(row.get("telephone")),
            "Immatriculation": _safe_text(row.get("Immatriculation")),
            "Police": _safe_text(row.get("Police")),
            "Campagne": _safe_text(row.get("Campagne")),
            "Reception": _safe_text(row.get("Reception")) or "REN",
            "Prise d'appel": _safe_text(row.get("Prise d'appel")) or "Oui",
            "Produit existant": _safe_text(row.get("Produit existant")),
            "Produit proposé": _safe_text(row.get("Produit proposé")),
            "Produit souhaite": _safe_text(row.get("Produit souhaite")),
            "Feedback": _safe_text(row.get("Feedback")),
            "CA": 0,
            "Point de vente": _safe_text(row.get("Point de vente")),
            "Heure_appel": _safe_text(row.get("Heure_appel")),
            "Statut": _safe_text(row.get("Statut")),
            "Motif_non_reponse": _safe_text(row.get("Motif_non_reponse")),
            "Commentaire": _safe_text(row.get("Commentaire")),
            "Satisfaction": _safe_text(row.get("Satisfaction")),
            "Recommendation": _safe_text(row.get("Recommendation")),
        }

        values = {k: (None if pd.isna(v) else v) for k, v in values.items()}
        payload = {k: v for k, v in values.items() if v is not None}

        if not payload.get("TO") or not payload.get("Campagne") or not payload.get("Reception"):
            skipped += 1
            continue

        try:
            service.create_call(payload)
            inserted += 1
        except DatabaseError as exc:
            skipped += 1
            print(f"Erreur insertion: {exc}")

    print(f"Insertion terminée : {inserted} ligne(s) insérée(s), {skipped} ligne(s) ignorée(s).")


if __name__ == "__main__":
    insert_classeur4_to_supabase()
