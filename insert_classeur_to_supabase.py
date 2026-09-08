# -*- coding: utf-8 -*-
"""Insertion du fichier classeur.xlsx vers Supabase."""
from __future__ import annotations

import os
from datetime import datetime, date
import pandas as pd
from database_service import DatabaseConfig, DatabaseService, DatabaseError


EXCEL_PATH = r"C:\Users\houno\Downloads\classeur.xlsx"
SECRETS_PATH = os.path.join(
    os.path.dirname(__file__), ".streamlit", "secrets.toml"
)


def _load_secrets(path: str) -> dict:
    import tomllib
    with open(path, "rb") as f:
        return tomllib.load(f)


def _to_date(val):
    if val is None:
        return None
    if isinstance(val, date):
        return val.isoformat()
    if isinstance(val, datetime):
        return val.date().isoformat()
    text = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def insert_classeur_to_supabase():
    secrets = _load_secrets(SECRETS_PATH)
    database_cfg = DatabaseConfig.from_mapping(secrets.get("database", {}))
    service = DatabaseService(database_cfg)

    df = pd.read_excel(EXCEL_PATH, sheet_name="Feuil1")
    df.columns = [str(col).strip() for col in df.columns]

    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        values = {
            "Date": _to_date(row.get("DATES") or row.get("Date")),
            "TO": row.get("TO"),
            "Nom du Client": None,
            "telephone": row.get("Telephone"),
            "Immatriculation": None,
            "Police": row.get("N°Police"),
            "Campagne": row.get("CAMPAGNE ACTIVE"),
            "Reception": row.get("Code Mouvement"),
            "Prise d'appel": None,
            "Produit existant": row.get("Produit"),
            "Produit proposé": None,
            "Produit souhaite": None,
            "Point de vente": row.get("Point De vente"),
            "Heure_appel": None,
            "Statut": None,
            "Motif_non_reponse": None,
            "Satisfaction": row.get("SATISFACTION"),
            "Recommendation": row.get("RECOMMANDATION"),
            "Feedback": None,
            "Commentaire": row.get("COMMENTAIRE"),
            "CA": 0,
        }
        values = {k: (None if pd.isna(v) else v) for k, v in values.items()}
        if not values.get("TO") or not values.get("Campagne") or not values.get("Reception"):
            skipped += 1
            continue
        try:
            service.create_call(values)
            inserted += 1
        except DatabaseError as exc:
            skipped += 1
            print(f"Erreur insertion: {exc}")

    print(f"Insertion classeur terminée : {inserted} ligne(s) insérée(s), {skipped} ligne(s) ignorée(s).")


if __name__ == "__main__":
    insert_classeur_to_supabase()
