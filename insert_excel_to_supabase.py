# -*- coding: utf-8 -*-
"""Insertion des données du fichier Excel vers Supabase."""
from __future__ import annotations

import os
from datetime import datetime, time
import pandas as pd
from database_service import DatabaseConfig, DatabaseService, DatabaseError


EXCEL_PATH = r"C:\Users\houno\Downloads\appels_export_2026-09-08.xlsx"
SECRETS_PATH = os.path.join(
    os.path.dirname(__file__), ".streamlit", "secrets.toml"
)


def _load_secrets(path: str) -> dict:
    import tomllib
    with open(path, "rb") as f:
        return tomllib.load(f)


def _parse_time(value):
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime("%H:%M")
    text = str(value)
    try:
        return datetime.strptime(text, "%H:%M:%S").strftime("%H:%M")
    except ValueError:
        pass
    try:
        return datetime.strptime(text, "%H:%M").strftime("%H:%M")
    except ValueError:
        pass
    return None


def _serialise(values):
    payload = {}
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(value, time):
            payload[key] = _parse_time(value)
        elif isinstance(value, datetime):
            payload[key] = value.date().isoformat()
        else:
            payload[key] = value
    return payload


def insert_excel_to_supabase():
    secrets = _load_secrets(SECRETS_PATH)
    database_cfg = DatabaseConfig.from_mapping(secrets.get("database", {}))
    service = DatabaseService(database_cfg)

    df = pd.read_excel(EXCEL_PATH, sheet_name="Call")
    df.columns = [str(col).strip() for col in df.columns]

    # Nettoyage des types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Heure_appel"] = df["Heure_appel"].apply(_parse_time)
    df["CA"] = pd.to_numeric(df["CA"], errors="coerce").fillna(0)

    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        values = {
            "Date": row.get("Date").date().isoformat() if pd.notna(row.get("Date")) else None,
            "TO": row.get("TO"),
            "Nom du Client": row.get("Nom du Client"),
            "telephone": row.get("telephone"),
            "Immatriculation": row.get("Immatriculation"),
            "Police": row.get("Police"),
            "Campagne": row.get("Campagne"),
            "Reception": row.get("Reception"),
            "Prise d'appel": row.get("Prise d'appel"),
            "Produit existant": row.get("Produit existant"),
            "Produit proposé": row.get("Produit proposé"),
            "Produit souhaite": row.get("Produit souhaite"),
            "Point de vente": row.get("Point de vente"),
            "Heure_appel": row.get("Heure_appel"),
            "Statut": row.get("Statut"),
            "Motif_non_reponse": row.get("Motif_non_reponse"),
            "Satisfaction": row.get("Satisfaction"),
            "Recommendation": row.get("Recommendation"),
            "Feedback": row.get("Feedback"),
            "Commentaire": row.get("Commentaire"),
            "CA": row.get("CA"),
        }
        values = {k: (None if pd.isna(v) else v) for k, v in values.items()}
        payload = _serialise(values)
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
    insert_excel_to_supabase()
