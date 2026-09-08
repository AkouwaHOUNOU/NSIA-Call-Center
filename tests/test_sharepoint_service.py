from datetime import date

import pytest

from sharepoint_service import (
    CALL_FIELDS,
    REFERENCE_FIELDS,
    SharePointConfig,
    SharePointConfigurationError,
    SharePointService,
    values_for_type,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.content = b"" if payload is None else b"{}"

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = []
        self.call_columns = {
            display: ("Title" if display == "Nom du Client" else f"CallField{i}")
            for i, display in enumerate(CALL_FIELDS.values(), start=1)
        }
        self.reference_columns = {
            display: ("Title" if display == "Valeur" else f"RefField{i}")
            for i, display in enumerate(REFERENCE_FIELDS.values(), start=1)
        }

    @staticmethod
    def _columns(mapping):
        return {
            "value": [
                {"name": internal, "displayName": display, "hidden": False}
                for display, internal in mapping.items()
            ]
        }

    def request(self, method, url, json=None, headers=None, timeout=None):
        self.calls.append(
            {"method": method, "url": url, "json": json, "headers": headers}
        )
        if url.endswith("sites/assurancesnsia.sharepoint.com:/sites/NSIACallCenter"):
            return FakeResponse(payload={"id": "site-test"})
        if "/sites/site-test/lists?$select=" in url:
            return FakeResponse(
                payload={
                    "value": [
                        {"id": "calls-id", "name": "APPELS_CALL_CENTER", "displayName": "APPELS_CALL_CENTER"},
                        {"id": "refs-id", "name": "REFERENCES_CALL_CENTER", "displayName": "REFERENCES_CALL_CENTER"},
                    ]
                }
            )
        if "/lists/calls-id/columns?" in url:
            return FakeResponse(payload=self._columns(self.call_columns))
        if "/lists/refs-id/columns?" in url:
            return FakeResponse(payload=self._columns(self.reference_columns))
        if method == "GET" and "/lists/calls-id/items?" in url:
            return FakeResponse(
                payload={
                    "value": [
                        {
                            "id": "42",
                            "eTag": '"42,1"',
                            "fields": {
                                self.call_columns["Nom du Client"]: "CLIENT FICTIF",
                                self.call_columns["Date Appel"]: "2026-09-03",
                                self.call_columns["CA"]: 1000,
                            },
                        }
                    ]
                }
            )
        if method == "GET" and "/lists/refs-id/items?" in url:
            return FakeResponse(
                payload={
                    "value": [
                        {
                            "id": "7",
                            "eTag": '"7,1"',
                            "fields": {
                                self.reference_columns["Valeur"]: "FLORENTINA",
                                self.reference_columns["TypeReference"]: "TO",
                                self.reference_columns["Actif"]: True,
                                self.reference_columns["Ordre"]: 3,
                            },
                        }
                    ]
                }
            )
        if method == "POST" and "/lists/calls-id/items" in url:
            return FakeResponse(status_code=201, payload={"id": "99"})
        if method in {"PATCH", "DELETE"}:
            return FakeResponse(status_code=204)
        raise AssertionError(f"Requête fictive non prévue : {method} {url}")


@pytest.fixture()
def service():
    config = SharePointConfig(
        tenant_id="tenant-test",
        client_id="client-test",
        client_secret="secret-test",
        site_url="https://assurancesnsia.sharepoint.com/sites/NSIACallCenter",
    )
    session = FakeSession()
    return SharePointService(config, session=session, token_provider=lambda: "token-test")


def test_configuration_refuse_les_secrets_manquants():
    with pytest.raises(SharePointConfigurationError):
        SharePointConfig.from_mapping({"tenant_id": "tenant-test"})


def test_creation_appel_utilise_les_noms_internes(service):
    created = service.create_call(
        {
            "Date": date(2026, 9, 3),
            "Nom du Client": "CLIENT FICTIF",
            "TO": "FLORENTINA",
            "CA": 1000,
        }
    )
    assert created["id"] == "99"
    post = next(call for call in service.session.calls if call["method"] == "POST")
    fields = post["json"]["fields"]
    assert fields["Title"] == "CLIENT FICTIF"
    assert fields[service.session.call_columns["Date Appel"]] == "2026-09-03"
    assert fields[service.session.call_columns["CA"]] == 1000


def test_lecture_appels_reconstruit_les_noms_de_l_application(service):
    rows = service.list_calls()
    assert rows[0]["_item_id"] == "42"
    assert rows[0]["Nom du Client"] == "CLIENT FICTIF"
    assert rows[0]["CA"] == 1000


def test_references_actives_et_filtrage_par_type(service):
    rows = service.list_references()
    assert values_for_type(rows, "TO") == ["FLORENTINA"]
    assert rows[0]["Actif"] is True


def test_modification_utilise_etag_et_nom_interne(service):
    service.update_call(
        "42",
        {"Nom du Client": "CLIENT FICTIF MODIFIE", "CA": 2000},
        etag='"42,1"',
    )
    patch = next(call for call in service.session.calls if call["method"] == "PATCH")
    assert patch["headers"]["If-Match"] == '"42,1"'
    assert patch["json"]["Title"] == "CLIENT FICTIF MODIFIE"
    assert patch["json"][service.session.call_columns["CA"]] == 2000

    service.update_call("42", {"Police": None})
    clear_patch = [
        call for call in service.session.calls if call["method"] == "PATCH"
    ][-1]
    assert clear_patch["json"][service.session.call_columns["Police"]] is None


def test_suppression_sans_etag_invalide(service):
    service.delete_call("42", etag=float("nan"))
    delete = next(call for call in service.session.calls if call["method"] == "DELETE")
    assert "If-Match" not in (delete["headers"] or {})
