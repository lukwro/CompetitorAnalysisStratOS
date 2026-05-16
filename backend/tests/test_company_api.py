from fastapi.testclient import TestClient

from app.main import app, companies


client = TestClient(app)


def setup_function() -> None:
    companies.clear()


def test_create_company_success() -> None:
    response = client.post("/api/company", json={"nip": "1234567890"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["nip"] == "1234567890"


def test_create_company_trims_whitespace() -> None:
    response = client.post("/api/company", json={"nip": "   1234567890   "})

    assert response.status_code == 201
    assert response.json()["nip"] == "1234567890"


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
