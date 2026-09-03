"""Accès sécurisé aux listes SharePoint de NSIA via Microsoft Graph.

Le module ne connaît aucun secret en dur. Les identifiants sont injectés depuis
``st.secrets`` par l'application Streamlit. Les noms internes SharePoint sont
résolus dynamiquement à partir des noms d'affichage afin de fonctionner même
quand la colonne ``Title`` a été renommée en ``Nom du Client`` ou ``Valeur``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
import time
import unicodedata
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlparse

import msal
import requests


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"


CALL_FIELDS: dict[str, str] = {
    "Date": "Date Appel",
    "TO": "TO",
    "Nom du Client": "Nom du Client",
    "telephone": "Numero de telephone",
    "Immatriculation": "Immatriculation",
    "Police": "Police",
    "Campagne": "Campagne",
    "Reception": "Reception",
    "Prise d'appel": "Prise Appel",
    "Produit existant": "Produit Existant",
    "Produit proposé": "Produit Propose",
    "Produit souhaite": "Produit Souhaite",
    "Point de vente": "Point de Vente",
    "Heure_appel": "Heure Appel",
    "Statut": "Statut",
    "Motif_non_reponse": "Motif Non Reponse",
    "Satisfaction": "Satisfaction",
    "Recommendation": "Recommendation",
    "Feedback": "Feedback",
    "Commentaire": "Commentaire",
    "CA": "CA",
}

REFERENCE_FIELDS: dict[str, str] = {
    "Valeur": "Valeur",
    "TypeReference": "TypeReference",
    "Actif": "Actif",
    "Ordre": "Ordre",
}


def _normaliser_nom(value: Any) -> str:
    """Normalise un nom d'affichage pour des correspondances robustes."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def _serialiser(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    # Les scalaires pandas/numpy exposent souvent item().
    if hasattr(value, "item") and callable(value.item):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return value


@dataclass(frozen=True)
class SharePointConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    site_url: str
    calls_list: str = "APPELS_CALL_CENTER"
    references_list: str = "REFERENCES_CALL_CENTER"
    timeout_seconds: int = 30

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "SharePointConfig":
        required = ("tenant_id", "client_id", "client_secret", "site_url")
        missing = [key for key in required if not str(values.get(key, "")).strip()]
        if missing:
            raise SharePointConfigurationError(
                "Configuration SharePoint incomplète : " + ", ".join(missing)
            )
        return cls(
            tenant_id=str(values["tenant_id"]).strip(),
            client_id=str(values["client_id"]).strip(),
            client_secret=str(values["client_secret"]).strip(),
            site_url=str(values["site_url"]).strip().rstrip("/"),
            calls_list=str(values.get("calls_list", "APPELS_CALL_CENTER")).strip(),
            references_list=str(
                values.get("references_list", "REFERENCES_CALL_CENTER")
            ).strip(),
            timeout_seconds=int(values.get("timeout_seconds", 30)),
        )


class SharePointError(RuntimeError):
    """Erreur fonctionnelle ou réseau sans exposition des secrets."""


class SharePointConfigurationError(SharePointError):
    """Configuration absente ou invalide."""


class SharePointService:
    """Client minimal Microsoft Graph pour les deux listes de l'application."""

    def __init__(
        self,
        config: SharePointConfig,
        *,
        session: requests.Session | None = None,
        token_provider: Callable[[], str] | None = None,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()
        self._token_provider = token_provider
        self._token: str | None = None
        self._token_expiry = 0.0
        self._site_id: str | None = None
        self._list_ids: dict[str, str] = {}
        self._column_maps: dict[str, dict[str, str]] = {}

        self._msal_app = None
        if token_provider is None:
            authority = f"https://login.microsoftonline.com/{config.tenant_id}"
            self._msal_app = msal.ConfidentialClientApplication(
                client_id=config.client_id,
                client_credential=config.client_secret,
                authority=authority,
            )

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "SharePointService":
        return cls(SharePointConfig.from_mapping(values))

    def _get_token(self, force_refresh: bool = False) -> str:
        if self._token_provider is not None:
            token = self._token_provider()
            if not token:
                raise SharePointError("Impossible d'obtenir le jeton Microsoft Graph.")
            return token

        if not force_refresh and self._token and time.time() < self._token_expiry:
            return self._token

        assert self._msal_app is not None
        result = self._msal_app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        token = result.get("access_token")
        if not token:
            code = result.get("error", "authentication_error")
            description = result.get("error_description", "Authentification refusée.")
            raise SharePointError(f"Microsoft Graph : {code} — {description[:240]}")

        self._token = str(token)
        lifetime = max(int(result.get("expires_in", 3600)) - 120, 60)
        self._token_expiry = time.time() + lifetime
        return self._token

    def _request(
        self,
        method: str,
        path_or_url: str,
        *,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        retry_auth: bool = True,
    ) -> requests.Response:
        url = (
            path_or_url
            if path_or_url.startswith("https://")
            else f"{GRAPH_ROOT}/{path_or_url.lstrip('/')}"
        )
        request_headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Accept": "application/json",
        }
        if json is not None:
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method,
                url,
                json=json,
                headers=request_headers,
                timeout=self.config.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise SharePointError(
                "Connexion à SharePoint impossible. Vérifiez Internet puis réessayez."
            ) from exc

        if response.status_code == 401 and retry_auth and self._token_provider is None:
            self._get_token(force_refresh=True)
            return self._request(
                method,
                path_or_url,
                json=json,
                headers=headers,
                retry_auth=False,
            )

        if response.status_code >= 400:
            code = f"HTTP {response.status_code}"
            message = "Opération SharePoint refusée."
            try:
                error = response.json().get("error", {})
                code = str(error.get("code") or code)
                message = str(error.get("message") or message)
            except (ValueError, AttributeError):
                pass
            raise SharePointError(f"{code} — {message[:300]}")
        return response

    def _get_json(self, path_or_url: str) -> dict[str, Any]:
        response = self._request("GET", path_or_url)
        try:
            return response.json()
        except ValueError as exc:
            raise SharePointError("Réponse SharePoint illisible.") from exc

    def _collect(self, path_or_url: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        next_url: str | None = path_or_url
        while next_url:
            payload = self._get_json(next_url)
            results.extend(payload.get("value", []))
            next_url = payload.get("@odata.nextLink")
        return results

    def _resolve_site_id(self) -> str:
        if self._site_id:
            return self._site_id
        parsed = urlparse(self.config.site_url)
        if parsed.scheme != "https" or not parsed.netloc or not parsed.path:
            raise SharePointConfigurationError("L'adresse du site SharePoint est invalide.")
        payload = self._get_json(f"sites/{parsed.netloc}:{parsed.path}")
        site_id = payload.get("id")
        if not site_id:
            raise SharePointError("Site SharePoint NSIA introuvable.")
        self._site_id = str(site_id)
        return self._site_id

    @staticmethod
    def _if_match_headers(etag: Any) -> dict[str, str] | None:
        """Construit un en-tête de concurrence uniquement pour un ETag valide."""
        if not isinstance(etag, str) or not etag.strip():
            return None
        return {"If-Match": etag.strip()}

    def _resolve_list_id(self, display_name: str) -> str:
        if display_name in self._list_ids:
            return self._list_ids[display_name]
        site_id = self._resolve_site_id()
        lists = self._collect(f"sites/{site_id}/lists?$select=id,name,displayName")
        wanted = _normaliser_nom(display_name)
        for item in lists:
            if wanted in {
                _normaliser_nom(item.get("displayName")),
                _normaliser_nom(item.get("name")),
            }:
                self._list_ids[display_name] = str(item["id"])
                return self._list_ids[display_name]
        raise SharePointError(f"Liste SharePoint introuvable : {display_name}")

    def _column_map(self, list_name: str) -> dict[str, str]:
        """Retourne nom d'affichage normalisé -> nom interne Graph."""
        if list_name in self._column_maps:
            return self._column_maps[list_name]
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(list_name)
        columns = self._collect(
            f"sites/{site_id}/lists/{list_id}/columns?$select=name,displayName,hidden"
        )
        mapping: dict[str, str] = {}
        for column in columns:
            internal = column.get("name")
            display = column.get("displayName")
            if internal:
                mapping[_normaliser_nom(internal)] = str(internal)
            if internal and display:
                mapping[_normaliser_nom(display)] = str(internal)
        self._column_maps[list_name] = mapping
        return mapping

    def _internal_fields(
        self,
        list_name: str,
        field_spec: Mapping[str, str],
        values: Mapping[str, Any],
        *,
        include_nulls: bool = False,
    ) -> dict[str, Any]:
        column_map = self._column_map(list_name)
        result: dict[str, Any] = {}
        missing: list[str] = []
        for canonical, value in values.items():
            if canonical.startswith("_") or canonical not in field_spec:
                continue
            display_name = field_spec[canonical]
            internal = column_map.get(_normaliser_nom(display_name))
            if not internal:
                missing.append(display_name)
                continue
            serialised = _serialiser(value)
            if serialised is not None or include_nulls:
                result[internal] = serialised
        if missing:
            raise SharePointConfigurationError(
                "Colonnes SharePoint introuvables : " + ", ".join(sorted(set(missing)))
            )
        return result

    def _canonical_fields(
        self,
        list_name: str,
        field_spec: Mapping[str, str],
        raw_fields: Mapping[str, Any],
    ) -> dict[str, Any]:
        column_map = self._column_map(list_name)
        result: dict[str, Any] = {}
        for canonical, display_name in field_spec.items():
            internal = column_map.get(_normaliser_nom(display_name))
            result[canonical] = raw_fields.get(internal) if internal else None
        return result

    def list_calls(self) -> list[dict[str, Any]]:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.calls_list)
        items = self._collect(
            f"sites/{site_id}/lists/{list_id}/items?$expand=fields&$top=999"
        )
        records: list[dict[str, Any]] = []
        for item in items:
            record = self._canonical_fields(
                self.config.calls_list, CALL_FIELDS, item.get("fields", {})
            )
            record["_item_id"] = str(item.get("id", ""))
            record["_etag"] = item.get("eTag") or item.get("@odata.etag")
            records.append(record)
        return records

    def create_call(self, values: Mapping[str, Any]) -> dict[str, Any]:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.calls_list)
        fields = self._internal_fields(
            self.config.calls_list, CALL_FIELDS, values
        )
        response = self._request(
            "POST",
            f"sites/{site_id}/lists/{list_id}/items",
            json={"fields": fields},
        )
        return response.json() if response.content else {}

    def update_call(
        self,
        item_id: str,
        values: Mapping[str, Any],
        *,
        etag: str | None = None,
    ) -> None:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.calls_list)
        fields = self._internal_fields(
            self.config.calls_list,
            CALL_FIELDS,
            values,
            include_nulls=True,
        )
        headers = self._if_match_headers(etag)
        self._request(
            "PATCH",
            f"sites/{site_id}/lists/{list_id}/items/{item_id}/fields",
            json=fields,
            headers=headers,
        )

    def delete_call(self, item_id: str, *, etag: str | None = None) -> None:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.calls_list)
        headers = self._if_match_headers(etag)
        self._request(
            "DELETE",
            f"sites/{site_id}/lists/{list_id}/items/{item_id}",
            headers=headers,
        )

    def list_references(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.references_list)
        items = self._collect(
            f"sites/{site_id}/lists/{list_id}/items?$expand=fields&$top=999"
        )
        records: list[dict[str, Any]] = []
        for item in items:
            record = self._canonical_fields(
                self.config.references_list,
                REFERENCE_FIELDS,
                item.get("fields", {}),
            )
            actif = record.get("Actif")
            record["Actif"] = True if actif is None else bool(actif)
            record["_item_id"] = str(item.get("id", ""))
            record["_etag"] = item.get("eTag") or item.get("@odata.etag")
            if include_inactive or record["Actif"]:
                records.append(record)
        return sorted(
            records,
            key=lambda row: (
                str(row.get("TypeReference") or ""),
                float(row.get("Ordre") or 999999),
                str(row.get("Valeur") or "").casefold(),
            ),
        )

    def add_reference(self, reference_type: str, value: str, order: int | None = None) -> str:
        reference_type = str(reference_type or "").strip().upper()
        value = str(value or "").strip()
        if not reference_type or not value:
            raise SharePointError("Le type et la valeur de référence sont obligatoires.")

        existing = self.list_references(include_inactive=True)
        for row in existing:
            if (
                str(row.get("TypeReference") or "").strip().upper() == reference_type
                and str(row.get("Valeur") or "").strip().casefold() == value.casefold()
            ):
                if row.get("Actif"):
                    return "existe"
                self._update_reference(row["_item_id"], {"Actif": True})
                return "reactive"

        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.references_list)
        values: dict[str, Any] = {
            "Valeur": value,
            "TypeReference": reference_type,
            "Actif": True,
        }
        if order is not None:
            values["Ordre"] = int(order)
        fields = self._internal_fields(
            self.config.references_list, REFERENCE_FIELDS, values
        )
        self._request(
            "POST",
            f"sites/{site_id}/lists/{list_id}/items",
            json={"fields": fields},
        )
        return "ajoute"

    def _update_reference(
        self,
        item_id: str,
        values: Mapping[str, Any],
        *,
        etag: str | None = None,
    ) -> None:
        site_id = self._resolve_site_id()
        list_id = self._resolve_list_id(self.config.references_list)
        fields = self._internal_fields(
            self.config.references_list, REFERENCE_FIELDS, values
        )
        headers = self._if_match_headers(etag)
        self._request(
            "PATCH",
            f"sites/{site_id}/lists/{list_id}/items/{item_id}/fields",
            json=fields,
            headers=headers,
        )

    def deactivate_reference(self, item_id: str, *, etag: str | None = None) -> None:
        self._update_reference(item_id, {"Actif": False}, etag=etag)

    def healthcheck(self) -> dict[str, str]:
        """Vérifie l'accès sans lire ni journaliser de donnée cliente."""
        site_id = self._resolve_site_id()
        self._resolve_list_id(self.config.calls_list)
        self._resolve_list_id(self.config.references_list)
        for list_name, fields in (
            (self.config.calls_list, CALL_FIELDS),
            (self.config.references_list, REFERENCE_FIELDS),
        ):
            column_map = self._column_map(list_name)
            missing = [
                display_name
                for display_name in fields.values()
                if _normaliser_nom(display_name) not in column_map
            ]
            if missing:
                raise SharePointConfigurationError(
                    f"Colonnes manquantes dans {list_name} : "
                    + ", ".join(sorted(set(missing)))
                )
        return {"status": "ok", "site_id": site_id}


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
