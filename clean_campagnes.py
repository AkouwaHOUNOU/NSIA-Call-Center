# -*- coding: utf-8 -*-
"""Nettoie les valeurs de campagne en supprimant les espaces superflus."""
from __future__ import annotations

import os
from database_service import DatabaseConfig, DatabaseService


SECRETS_PATH = os.path.join(
    os.path.dirname(__file__), ".streamlit", "secrets.toml"
)


def _load_secrets(path: str) -> dict:
    import tomllib

    with open(path, "rb") as f:
        return tomllib.load(f)


def clean_campagnes():
    secrets = _load_secrets(SECRETS_PATH)
    cfg = DatabaseConfig.from_mapping(secrets["database"])
    service = DatabaseService(cfg)

    rows = service.list_calls()
    updates = []
    for row in rows:
        campagne = row.get("Campagne")
        if isinstance(campagne, str) and campagne.strip() != campagne:
            updates.append(
                {
                    "item_id": row.get("_item_id"),
                    "etag": row.get("_etag"),
                    "campagne": campagne.strip(),
                }
            )

    if not updates:
        print("Aucune campagne à corriger.")
        return

    for item in updates:
        service.update_call(
            item["item_id"],
            {"Campagne": item["campagne"]},
            etag=item["etag"],
        )
    print(f"Nettoyage terminé : {len(updates)} campagne(s) corrigée(s).")


if __name__ == "__main__":
    clean_campagnes()
