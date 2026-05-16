from fastapi.testclient import TestClient

from app.main import app, companies


client = TestClient(app)


def setup_function() -> None:
    companies.clear()


def test_create_company_success() -> None:
    response = client.post("/api/company", json={"name": "Acme"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Acme"


def test_create_company_trims_whitespace() -> None:
    response = client.post("/api/company", json={"name": "   Acme   "})

    assert response.status_code == 201
    assert response.json()["name"] == "Acme"


def test_create_company_rejects_empty_value() -> None:
    response = client.post("/api/company", json={"name": "   "})

    assert response.status_code == 422
    assert "wymagane" in response.json()["detail"].lower()


def test_create_company_accepts_200_characters() -> None:
    name = "A" * 200
    response = client.post("/api/company", json={"name": name})

    assert response.status_code == 201
    assert response.json()["name"] == name


def test_create_company_rejects_above_200_characters() -> None:
    response = client.post("/api/company", json={"name": "A" * 201})

    assert response.status_code == 422
    assert "200" in response.json()["detail"]
