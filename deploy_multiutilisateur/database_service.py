"""Stockage persistant Supabase pour l'application NSIA Call Center.

Les secrets Supabase sont fournis par ``st.secrets`` dans l'application. Ce
module ne contient aucun identifiant en dur et n'expose jamais la clé secrète
dans les messages d'erreur.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
import base64
import json
import math
import re
from typing import Any, Iterable, Mapping

from supabase import Client, create_client


CALL_FIELDS: dict[str, str] = {
    "Date": "call_date",
    "TO": "to_name",
    "Nom du Client": "client_name",
    "telephone": "phone",
    "Immatriculation": "registration_number",
    "Police": "policy_number",
    "Campagne": "campaign",
    "Reception": "reception",
    "Prise d'appel": "call_answer",
    "Produit existant": "existing_product",
    "Produit proposé": "proposed_product",
    "Produit souhaite": "desired_product",
    "Point de vente": "point_of_sale",
    "Heure_appel": "call_time",
    "Statut": "status",
    "Motif_non_reponse": "no_answer_reason",
    "Satisfaction": "satisfaction",
    "Recommendation": "recommendation",
    "Feedback": "feedback",
    "Commentaire": "comment",
    "CA": "revenue",
}

REFERENCE_FIELDS: dict[str, str] = {
    "Valeur": "value",
    "TypeReference": "reference_type",
    "Actif": "active",
    "Ordre": "sort_order",
}


class DatabaseError(RuntimeError):
    """Erreur fonctionnelle ou réseau sans exposition des secrets."""


class DatabaseConfigurationError(DatabaseError):
    """Configuration absente ou invalide."""


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    secret_key: str
    calls_table: str = "appels_call_center"
    references_table: str = "references_call_center"

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "DatabaseConfig":
        url = str(values.get("url", "")).strip()
        secret_key = str(
            values.get("secret_key") or values.get("service_role_key") or ""
        ).strip()
        missing = []
        if not url:
            missing.append("url")
        if not secret_key:
            missing.append("secret_key")
        if missing:
            raise DatabaseConfigurationError(
                "Configuration Supabase incomplète : " + ", ".join(missing)
            )
        if not url.startswith("https://"):
            raise DatabaseConfigurationError("L'URL Supabase doit commencer par https://.")
        if secret_key.startswith("sb_publishable_") or _legacy_jwt_role(secret_key) in {
            "anon",
            "authenticated",
        }:
            raise DatabaseConfigurationError(
                "La clé publique Supabase n'est pas autorisée. Utilisez uniquement "
                "la clé secrète du serveur."
            )

        calls_table = _valid_table_name(
            values.get("calls_table", "appels_call_center")
        )
        references_table = _valid_table_name(
            values.get("references_table", "references_call_center")
        )
        return cls(
            url=url,
            secret_key=secret_key,
            calls_table=calls_table,
            references_table=references_table,
        )


def _valid_table_name(value: Any) -> str:
    name = str(value or "").strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", name):
        raise DatabaseConfigurationError(f"Nom de table Supabase invalide : {name!r}")
    return name


def _legacy_jwt_role(value: str) -> str | None:
    """Lit seulement le rôle d'une ancienne clé JWT, sans valider ni exposer la clé."""
    parts = str(value).split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        return str(decoded.get("role") or "").strip().lower() or None
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return None


def _serialise(value: Any) -> Any:
    if value is None:
        return None
    try:
        if bool(math.isnan(value)):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    if hasattr(value, "item") and callable(value.item):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    return value


def _version_from_etag(etag: Any) -> int | None:
    if etag is None:
        return None
    try:
        if bool(math.isnan(etag)):
            return None
    except (TypeError, ValueError):
        pass
    match = re.search(r"\d+", str(etag))
    return int(match.group(0)) if match else None


class DatabaseService:
    """Accès minimal aux appels et aux références dans Supabase."""

    def __init__(self, config: DatabaseConfig, *, client: Client | None = None) -> None:
        self.config = config
        try:
            self.client = client or create_client(config.url, config.secret_key)
        except Exception as exc:
            raise DatabaseConfigurationError(
                "Initialisation Supabase impossible. Vérifiez l'URL et la clé secrète."
            ) from exc

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "DatabaseService":
        return cls(DatabaseConfig.from_mapping(values))

    @staticmethod
    def _data(response: Any) -> list[dict[str, Any]]:
        data = getattr(response, "data", None)
        if data is None:
            return []
        if isinstance(data, list):
            return [dict(row) for row in data]
        if isinstance(data, dict):
            return [dict(data)]
        return []

    def _execute(self, query: Any, action: str) -> list[dict[str, Any]]:
        try:
            return self._data(query.execute())
        except Exception as exc:
            raise DatabaseError(
                f"{action} impossible. Vérifiez la connexion à la base puis réessayez."
            ) from exc

    def _fetch_all(
        self,
        table_name: str,
        *,
        include_inactive: bool = True,
        order_column: str = "created_at",
        descending: bool = False,
    ) -> list[dict[str, Any]]:
        page_size = 1000
        start = 0
        rows: list[dict[str, Any]] = []
        while True:
            query = self.client.table(table_name).select("*")
            if not include_inactive:
                query = query.eq("active", True)
            query = query.order(order_column, desc=descending).range(
                start, start + page_size - 1
            )
            page = self._execute(query, "Lecture de la base")
            rows.extend(page)
            if len(page) < page_size:
                return rows
            start += page_size

    @staticmethod
    def _call_payload(values: Mapping[str, Any], *, include_nulls: bool) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for canonical, column in CALL_FIELDS.items():
            if canonical not in values:
                continue
            value = _serialise(values.get(canonical))
            if include_nulls or value is not None:
                payload[column] = value
        return payload

    @staticmethod
    def _canonical_call(row: Mapping[str, Any]) -> dict[str, Any]:
        result = {
            canonical: row.get(column) for canonical, column in CALL_FIELDS.items()
        }
        result["_item_id"] = str(row.get("id", ""))
        result["_etag"] = str(row.get("version", 1))
        return result

    def list_calls(self) -> list[dict[str, Any]]:
        rows = self._fetch_all(
            self.config.calls_table,
            order_column="created_at",
            descending=True,
        )
        return [self._canonical_call(row) for row in rows]

    def create_call(self, values: Mapping[str, Any]) -> dict[str, Any]:
        payload = self._call_payload(values, include_nulls=False)
        payload["version"] = 1
        rows = self._execute(
            self.client.table(self.config.calls_table).insert(payload),
            "Enregistrement de l'appel",
        )
        if not rows or not rows[0].get("id"):
            raise DatabaseError("La base n'a pas confirmé l'enregistrement de l'appel.")
        return {"id": str(rows[0]["id"]), **self._canonical_call(rows[0])}

    def _get_row(self, table_name: str, item_id: str) -> dict[str, Any]:
        rows = self._execute(
            self.client.table(table_name).select("*").eq("id", item_id).limit(1),
            "Lecture de l'enregistrement",
        )
        if not rows:
            raise DatabaseError("L'enregistrement demandé n'existe plus.")
        return rows[0]

    def _update_versioned(
        self,
        table_name: str,
        item_id: str,
        payload: Mapping[str, Any],
        *,
        etag: str | None,
    ) -> None:
        current = self._get_row(table_name, item_id)
        current_version = int(current.get("version") or 1)
        expected = _version_from_etag(etag)
        if expected is not None and expected != current_version:
            raise DatabaseError(
                "Cet enregistrement a été modifié par une autre personne. Actualisez la page."
            )
        update = dict(payload)
        update["version"] = current_version + 1
        query = (
            self.client.table(table_name)
            .update(update)
            .eq("id", item_id)
            .eq("version", current_version)
        )
        rows = self._execute(query, "Modification de l'enregistrement")
        if not rows:
            raise DatabaseError(
                "Modification non confirmée. Actualisez la page puis réessayez."
            )

    def update_call(
        self,
        item_id: str,
        values: Mapping[str, Any],
        *,
        etag: str | None = None,
    ) -> None:
        payload = self._call_payload(values, include_nulls=True)
        self._update_versioned(
            self.config.calls_table, item_id, payload, etag=etag
        )

    def delete_call(self, item_id: str, *, etag: str | None = None) -> None:
        current = self._get_row(self.config.calls_table, item_id)
        expected = _version_from_etag(etag)
        current_version = int(current.get("version") or 1)
        if expected is not None and expected != current_version:
            raise DatabaseError(
                "Cet enregistrement a été modifié par une autre personne. Actualisez la page."
            )
        query = (
            self.client.table(self.config.calls_table)
            .delete()
            .eq("id", item_id)
            .eq("version", current_version)
        )
        rows = self._execute(query, "Suppression de l'appel")
        if not rows:
            raise DatabaseError("La suppression n'a pas été confirmée.")

    @staticmethod
    def _canonical_reference(row: Mapping[str, Any]) -> dict[str, Any]:
        result = {
            canonical: row.get(column)
            for canonical, column in REFERENCE_FIELDS.items()
        }
        result["Actif"] = True if result.get("Actif") is None else bool(result["Actif"])
        result["_item_id"] = str(row.get("id", ""))
        result["_etag"] = str(row.get("version", 1))
        return result

    def list_references(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        rows = self._fetch_all(
            self.config.references_table,
            include_inactive=include_inactive,
            order_column="sort_order",
        )
        return [self._canonical_reference(row) for row in rows]

    def add_reference(
        self, reference_type: str, value: str, order: int | None = None
    ) -> str:
        reference_type = str(reference_type or "").strip().upper()
        value = str(value or "").strip()
        if not reference_type or not value:
            raise DatabaseError("Le type et la valeur de référence sont obligatoires.")

        existing = self.list_references(include_inactive=True)
        for row in existing:
            if (
                str(row.get("TypeReference") or "").strip().upper() == reference_type
                and str(row.get("Valeur") or "").strip().casefold() == value.casefold()
            ):
                if row.get("Actif"):
                    return "existe"
                self._update_versioned(
                    self.config.references_table,
                    row["_item_id"],
                    {"active": True},
                    etag=row.get("_etag"),
                )
                return "reactive"

        payload = {
            "value": value,
            "reference_type": reference_type,
            "active": True,
            "sort_order": int(order) if order is not None else 999999,
            "version": 1,
        }
        rows = self._execute(
            self.client.table(self.config.references_table).insert(payload),
            "Ajout de la référence",
        )
        if not rows:
            raise DatabaseError("L'ajout de la référence n'a pas été confirmé.")
        return "ajoute"

    def deactivate_reference(
        self, item_id: str, *, etag: str | None = None
    ) -> None:
        self._update_versioned(
            self.config.references_table,
            item_id,
            {"active": False},
            etag=etag,
        )

    def healthcheck(self) -> dict[str, str]:
        for table_name in (
            self.config.calls_table,
            self.config.references_table,
        ):
            self._execute(
                self.client.table(table_name).select("id").limit(1),
                "Test de connexion",
            )
        return {"status": "ok"}


def values_for_type(
    rows: Iterable[Mapping[str, Any]], reference_type: str
) -> list[str]:
    wanted = str(reference_type).strip().upper()
    values: list[str] = []
    for row in rows:
        if str(row.get("TypeReference") or "").strip().upper() != wanted:
            continue
        value = str(row.get("Valeur") or "").strip()
        if value and value.casefold() not in {item.casefold() for item in values}:
            values.append(value)
    return values
