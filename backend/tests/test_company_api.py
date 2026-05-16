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
    response_mock.text = '{"data":{"nazwa":"ACME SA"}}'
    response_mock.headers = {"content-type": "application/json", "server": "mock"}
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
    response_mock.text = "upstream unavailable"
    response_mock.headers = {"content-type": "text/plain", "server": "mock"}

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 502
    assert "niedostępne" in response.json()["detail"]


def test_create_company_returns_404_when_company_not_found() -> None:
    response_mock = Mock()
    response_mock.status_code = 404
    response_mock.text = "not found"
    response_mock.headers = {"content-type": "text/plain", "server": "mock"}

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 404
    assert "Nie znaleziono" in response.json()["detail"]


def test_create_company_returns_502_for_invalid_upstream_payload_shape() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.text = '["unexpected","shape"]'
    response_mock.headers = {"content-type": "application/json", "server": "mock"}
    response_mock.json.return_value = ["unexpected", "shape"]

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("httpx.Client.get", return_value=response_mock):
        response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 502
    assert "format" in response.json()["detail"].lower()


def test_openai_connection_test_success() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"data": []}

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.return_value = response_mock
        response = client.get("/api/openai/connection-test")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OK"
    assert "działa poprawnie" in body["detail"]


def test_openai_connection_test_without_api_key() -> None:
    with patch("app.main.OPENAI_API_KEY", ""):
        response = client.get("/api/openai/connection-test")

    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_openai_connection_test_timeout() -> None:
    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.side_effect = httpx.TimeoutException("timeout")
        response = client.get("/api/openai/connection-test")

    assert response.status_code == 504
    assert "Timeout" in response.json()["detail"]


def test_openai_connection_test_5xx() -> None:
    response_mock = Mock()
    response_mock.status_code = 503

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.return_value = response_mock
        response = client.get("/api/openai/connection-test")

    assert response.status_code == 502
    assert "niedostępne" in response.json()["detail"]


def test_openai_connection_test_invalid_payload_shape() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"unexpected": "shape"}

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.return_value = response_mock
        response = client.get("/api/openai/connection-test")

    assert response.status_code == 502
    assert "format" in response.json()["detail"].lower()


def test_find_competitors_success() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"competitors":[{"name":"Firma A","similarity_reason":"Ta sama grupa klientów","confidence":"HIGH"},{"name":"Firma B","similarity_reason":"Podobny model usługowy","confidence":"MEDIUM"},{"name":"Firma C","similarity_reason":"Zbliżony segment SMB","confidence":"LOW"}]}'
                }
            }
        ]
    }

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.post.return_value = response_mock
        response = client.post(
            "/api/competitors/find",
            json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania", "limit": 3},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["input_company"] == "Acme"
    assert body["input_main_activity"] == "Produkcja oprogramowania"
    assert len(body["competitors"]) == 3
    assert body["competitors"][0]["name"] == "Firma A"


def test_find_competitors_rejects_empty_company_name() -> None:
    response = client.post(
        "/api/competitors/find",
        json={"company_name": "   ", "main_activity": "Produkcja oprogramowania"},
    )

    assert response.status_code == 400
    assert "company_name" in response.json()["detail"]


def test_find_competitors_rejects_empty_main_activity() -> None:
    response = client.post(
        "/api/competitors/find",
        json={"company_name": "Acme", "main_activity": " "},
    )

    assert response.status_code == 400
    assert "main_activity" in response.json()["detail"]


def test_find_competitors_rejects_invalid_limit() -> None:
    response = client.post(
        "/api/competitors/find",
        json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania", "limit": 2},
    )

    assert response.status_code == 400
    assert "3-10" in response.json()["detail"]


def test_find_competitors_without_openai_model() -> None:
    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", ""):
        response = client.post(
            "/api/competitors/find",
            json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania"},
        )

    assert response.status_code == 500
    assert "OPENAI_MODEL" in response.json()["detail"]


def test_find_competitors_timeout() -> None:
    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.post.side_effect = httpx.TimeoutException("timeout")
        response = client.post(
            "/api/competitors/find",
            json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania"},
        )

    assert response.status_code == 504
    assert "Timeout" in response.json()["detail"]


def test_find_competitors_invalid_openai_payload_shape() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"unexpected": "shape"}

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.post.return_value = response_mock
        response = client.post(
            "/api/competitors/find",
            json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania"},
        )

    assert response.status_code == 502
    assert "format" in response.json()["detail"].lower()


def test_find_competitors_invalid_model_content_format() -> None:
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {
        "choices": [{"message": {"content": "to nie jest json"}}]
    }

    with patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.post.return_value = response_mock
        response = client.post(
            "/api/competitors/find",
            json={"company_name": "Acme", "main_activity": "Produkcja oprogramowania"},
        )

    assert response.status_code == 502
    assert "json" in response.json()["detail"].lower()


def test_combined_flow_success_two_step() -> None:
    rejestr_response = Mock()
    rejestr_response.status_code = 200
    rejestr_response.text = '{"data":{"nazwa":"ACME SA"}}'
    rejestr_response.headers = {"content-type": "application/json", "server": "mock"}
    rejestr_response.json.return_value = {
        "data": {
            "nazwa": "ACME SA",
            "status": "AKTYWNA",
            "miasto": "Warszawa",
            "adres": "ul. Prosta 1",
            "stan": {"pkd_przewazajace_dzial": "Produkcja oprogramowania"},
        }
    }

    openai_response = Mock()
    openai_response.status_code = 200
    openai_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"competitors":[{"name":"Firma A","similarity_reason":"Ta sama grupa klientów","confidence":"HIGH"},{"name":"Firma B","similarity_reason":"Podobny model usługowy","confidence":"MEDIUM"},{"name":"Firma C","similarity_reason":"Zbliżony segment SMB","confidence":"LOW"}]}'
                }
            }
        ]
    }

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.return_value = rejestr_response
        client_instance.post.return_value = openai_response

        company_response = client.post("/api/company", json={"nip": "1234567890"})
        assert company_response.status_code == 201
        company_body = company_response.json()

        competitors_response = client.post(
            "/api/competitors/find",
            json={
                "company_name": company_body["organization_name"],
                "main_activity": company_body["predominant_activity"],
                "limit": 5,
            },
        )

    assert competitors_response.status_code == 200
    competitors_body = competitors_response.json()
    assert len(competitors_body["competitors"]) >= 3


def test_combined_flow_partial_second_step_failure() -> None:
    rejestr_response = Mock()
    rejestr_response.status_code = 200
    rejestr_response.text = '{"data":{"nazwa":"ACME SA"}}'
    rejestr_response.headers = {"content-type": "application/json", "server": "mock"}
    rejestr_response.json.return_value = {
        "data": {
            "nazwa": "ACME SA",
            "status": "AKTYWNA",
            "miasto": "Warszawa",
            "adres": "ul. Prosta 1",
            "stan": {"pkd_przewazajace_dzial": "Produkcja oprogramowania"},
        }
    }

    openai_response = Mock()
    openai_response.status_code = 503
    openai_response.json.return_value = {"error": "upstream unavailable"}

    with patch("app.main.REJESTR_IO_API_KEY", "test-key"), patch("app.main.OPENAI_API_KEY", "openai-key"), patch("app.main.OPENAI_MODEL", "gpt-4o-mini"), patch("app.main.httpx.Client") as client_mock:
        client_instance = client_mock.return_value.__enter__.return_value
        client_instance.get.return_value = rejestr_response
        client_instance.post.return_value = openai_response

        company_response = client.post("/api/company", json={"nip": "1234567890"})
        assert company_response.status_code == 201
        company_body = company_response.json()

        competitors_response = client.post(
            "/api/competitors/find",
            json={
                "company_name": company_body["organization_name"],
                "main_activity": company_body["predominant_activity"],
                "limit": 5,
            },
        )

    assert competitors_response.status_code == 502
    assert "niedostępne" in competitors_response.json()["detail"].lower()
