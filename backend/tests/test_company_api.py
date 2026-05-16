from unittest.mock import Mock, patch

import httpx
from fastapi.testclient import TestClient

from app.main import app, companies, map_rejestr_payload


client = TestClient(app)


def setup_function() -> None:
    companies.clear()


def test_map_rejestr_payload_with_krd() -> None:
    payload = {
        "data": {
            "nazwa": "ACME SA",
            "status": "AKTYWNA",
            "miasto": "Warszawa",
            "adres": "ul. Prosta 1",
            "krd": "BRAK WPISU",
        }
    }

    mapped = map_rejestr_payload(payload, "1234567890")

    assert mapped["nip"] == "1234567890"
    assert mapped["organization_name"] == "ACME SA"
    assert mapped["organization_status"] == "AKTYWNA"
    assert mapped["city"] == "Warszawa"
    assert mapped["address"] == "ul. Prosta 1"
    assert mapped["krd_status"] == "BRAK WPISU"


def test_map_rejestr_payload_with_nested_address_object() -> None:
    payload = {
        "data": {
            "nazwa": "ACME SA",
            "status": "AKTYWNA",
            "adres": {
                "kod": "30-727",
                "miejscowosc": "Krakow",
                "ulica": "Pana Tadeusza",
            },
            "krd": "BRAK WPISU",
        }
    }

    mapped = map_rejestr_payload(payload, "1234567890")

    assert mapped["city"] == "Krakow"
    assert mapped["address"] == "30-727, Krakow, Pana Tadeusza"


def test_create_company_success() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {
        "data": {
            "nazwa": "ACME SA",
            "status": "AKTYWNA",
            "miasto": "Warszawa",
            "adres": "ul. Prosta 1",
            "krd": "BRAK WPISU",
        }
    }

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["nip"] == "1234567890"
    assert body["organization_name"] == "ACME SA"
    assert body["krd_status"] == "BRAK WPISU"


def test_create_company_rejects_empty_value() -> None:
    response = client.post("/api/company", json={"nip": "   "})

    assert response.status_code == 422
    assert "wymagane" in response.json()["detail"].lower()


def test_create_company_rejects_short_nip() -> None:
    response = client.post("/api/company", json={"nip": "123456789"})

    assert response.status_code == 422
    assert "10 cyfr" in response.json()["detail"]


def test_create_company_rejects_non_digit_nip() -> None:
    response = client.post("/api/company", json={"nip": "12345ABCDE"})

    assert response.status_code == 422
    assert "10 cyfr" in response.json()["detail"]


def test_create_company_returns_config_error_without_api_key() -> None:
    with patch("app.main.REJESTR_IO_API_KEY", ""):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 500
    assert "REJESTR_IO_API_KEY" in response.json()["detail"]


def test_create_company_returns_timeout_for_upstream_timeout() -> None:
    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", side_effect=httpx.TimeoutException("timeout")):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 504
    assert "Timeout" in response.json()["detail"]


def test_create_company_returns_502_for_upstream_5xx() -> None:
    response_mock = Mock()
    response_mock.status_code = 503

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 502
    assert "niedostępne" in response.json()["detail"]


def test_create_company_returns_404_when_company_not_found() -> None:
    response_mock = Mock()
    response_mock.status_code = 404

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 404
    assert "Nie znaleziono" in response.json()["detail"]


def test_create_company_returns_502_for_invalid_upstream_payload_shape() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = ["unexpected", "shape"]

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 502
    assert "format" in response.json()["detail"].lower()
