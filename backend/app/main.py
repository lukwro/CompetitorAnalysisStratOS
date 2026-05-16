import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

NIP_LENGTH = 10
REJESTR_IO_BASE_URL = os.getenv("REJESTR_IO_BASE_URL", "https://rejestr.io/api/v2")
REJESTR_IO_API_KEY = os.getenv("REJESTR_IO_API_KEY", "").strip()
REJESTR_IO_AUTH_SCHEME = os.getenv("REJESTR_IO_AUTH_SCHEME", "Bearer").strip()
REJESTR_IO_AUTH_FALLBACK_ENABLED = os.getenv("REJESTR_IO_AUTH_FALLBACK_ENABLED", "1").strip() == "1"
REJESTR_IO_TIMEOUT_SECONDS = float(os.getenv("REJESTR_IO_TIMEOUT_SECONDS", "10"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "10"))


class CompanyIn(BaseModel):
    nip: str


class CompanyOut(BaseModel):
    id: int
    nip: str
    organization_name: str | None = None
    organization_status: str | None = None
    predominant_activity: str | None = None
    city: str | None = None
    address: str | None = None
    krd_status: str | None = None
    debug: dict | None = None


class OpenAIConnectionOut(BaseModel):
    status: str
    detail: str
    provider: str = "openai"


app = FastAPI(title="CompetitorAnalysisStratOS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

companies: list[CompanyOut] = []
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def normalize_nip(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Pole 'NIP' jest wymagane.")
    if not normalized.isdigit() or len(normalized) != NIP_LENGTH:
        raise ValueError("NIP musi zawierać dokładnie 10 cyfr.")
    return normalized


def derive_organization_status(stan: dict | None, fallback: str | None) -> str | None:
    if not isinstance(stan, dict):
        return fallback

    if stan.get("czy_wykreslona") is True:
        return "Wykreślona"
    if stan.get("w_upadlosci") is True:
        return "W upadłości"
    if stan.get("w_likwidacji") is True:
        return "W likwidacji"
    if stan.get("w_zawieszeniu") is True:
        return "W zawieszeniu"
    return fallback or "Aktywna"


def map_rejestr_payload(payload: dict, nip: str) -> dict:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Nieprawidłowy format odpowiedzi z rejestr.io.")

    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Nieprawidłowy format danych organizacji z rejestr.io.")

    raw_address = data.get("adres") or data.get("address")
    if isinstance(raw_address, dict):
        address_parts = [
            raw_address.get("kod"),
            raw_address.get("miejscowosc"),
            raw_address.get("ulica"),
        ]
        address = ", ".join([part for part in address_parts if isinstance(part, str) and part.strip()]) or str(raw_address)
    elif isinstance(raw_address, str):
        address = raw_address
    else:
        address = data.get("ulica") if isinstance(data.get("ulica"), str) else None

    city = data.get("miasto") or data.get("miejscowosc") or data.get("city")
    if not isinstance(city, str) and isinstance(raw_address, dict):
        city = raw_address.get("miejscowosc")

    nazwy = data.get("nazwy") if isinstance(data.get("nazwy"), dict) else {}
    stan = data.get("stan") if isinstance(data.get("stan"), dict) else {}

    fallback_status = data.get("status") or data.get("status_podmiotu")
    status = derive_organization_status(stan, fallback_status if isinstance(fallback_status, str) else None)

    predominant_activity = stan.get("pkd_przewazajace_dzial") if isinstance(stan.get("pkd_przewazajace_dzial"), str) else None

    return {
        "nip": nip,
        "organization_name": data.get("nazwa") or data.get("nazwa_pelna") or nazwy.get("pelna") or nazwy.get("skrocona") or data.get("name"),
        "organization_status": status,
        "predominant_activity": predominant_activity,
        "city": city if isinstance(city, str) else None,
        "address": address,
        "krd_status": data.get("krd") or data.get("krd_status") or data.get("status_krd"),
    }


def build_authorization_value() -> str:
    if REJESTR_IO_AUTH_SCHEME:
        return f"{REJESTR_IO_AUTH_SCHEME} {REJESTR_IO_API_KEY}"
    return REJESTR_IO_API_KEY


def authorization_candidates() -> list[str]:
    primary = build_authorization_value()
    candidates = [primary]
    if REJESTR_IO_AUTH_FALLBACK_ENABLED and REJESTR_IO_AUTH_SCHEME and REJESTR_IO_API_KEY not in candidates:
        candidates.append(REJESTR_IO_API_KEY)
    return candidates


def fetch_rejestr_data(nip: str) -> tuple[dict, dict]:
    if not REJESTR_IO_API_KEY:
        raise HTTPException(status_code=500, detail="Brak konfiguracji REJESTR_IO_API_KEY.")

    url = f"{REJESTR_IO_BASE_URL.rstrip('/')}/org/nip{nip}"
    debug = {
        "request": {
            "method": "GET",
            "url": url,
            "auth_candidates": [
                (f"{REJESTR_IO_AUTH_SCHEME} ***" if i == 0 and REJESTR_IO_AUTH_SCHEME else "***")
                for i, _ in enumerate(authorization_candidates())
            ],
            "timeout_seconds": REJESTR_IO_TIMEOUT_SECONDS,
        }
    }

    try:
        with httpx.Client(timeout=REJESTR_IO_TIMEOUT_SECONDS) as client:
            response = None
            for auth_value in authorization_candidates():
                response = client.get(url, headers={"Authorization": auth_value, "Accept": "application/json"})
                if response.status_code not in (401, 403):
                    break
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Timeout podczas łączenia z rejestr.io.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Błąd połączenia z rejestr.io.") from exc

    if response is None:
        raise HTTPException(status_code=502, detail="Nie udało się uzyskać odpowiedzi z rejestr.io.")

    text_preview = response.text[:4000] if response.text else ""
    debug["response"] = {
        "status_code": response.status_code,
        "headers": {
            "content-type": response.headers.get("content-type"),
            "server": response.headers.get("server"),
        },
        "body_preview": text_preview,
    }

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Nie znaleziono danych organizacji dla podanego NIP.")
    if response.status_code in (401, 403):
        upstream_detail = None
        try:
            payload = response.json()
            if isinstance(payload, dict):
                upstream_detail = payload.get("message") or payload.get("detail") or payload.get("error")
        except ValueError:
            upstream_detail = response.text.strip() or None

        if upstream_detail:
            raise HTTPException(
                status_code=502,
                detail=f"Autoryzacja odrzucona przez rejestr.io (HTTP {response.status_code}): {upstream_detail}",
            )
        raise HTTPException(
            status_code=502,
            detail=f"Autoryzacja odrzucona przez rejestr.io (HTTP {response.status_code}).",
        )
    if response.status_code >= 500:
        raise HTTPException(status_code=502, detail="rejestr.io jest chwilowo niedostępne.")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Błąd odpowiedzi z rejestr.io (HTTP {response.status_code}).",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Nieprawidłowa odpowiedź JSON z rejestr.io.") from exc

    debug["response"]["json"] = payload
    return map_rejestr_payload(payload, nip), debug


def check_openai_connection() -> OpenAIConnectionOut:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Brak konfiguracji OPENAI_API_KEY.")

    url = f"{OPENAI_BASE_URL.rstrip('/')}/models"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=OPENAI_TIMEOUT_SECONDS) as client:
            response = client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Timeout podczas łączenia z OpenAI API.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Błąd połączenia z OpenAI API.") from exc

    if response.status_code >= 500:
        raise HTTPException(status_code=502, detail="OpenAI API jest chwilowo niedostępne.")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Błąd odpowiedzi z OpenAI API (HTTP {response.status_code}).")

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Nieprawidłowa odpowiedź JSON z OpenAI API.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise HTTPException(status_code=502, detail="Nieprawidłowy format odpowiedzi z OpenAI API.")

    return OpenAIConnectionOut(status="OK", detail="Połączenie z OpenAI API działa poprawnie.")


@app.post("/api/company", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyIn) -> CompanyOut:
    try:
        normalized_nip = normalize_nip(payload.nip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    company_data, debug = fetch_rejestr_data(normalized_nip)
    company = CompanyOut(id=len(companies) + 1, debug=debug, **company_data)
    companies.append(company)
    return company


@app.get("/api/companies", response_model=list[CompanyOut])
def list_companies() -> list[CompanyOut]:
    return companies


@app.get("/api/openai/connection-test", response_model=OpenAIConnectionOut)
def openai_connection_test() -> OpenAIConnectionOut:
    return check_openai_connection()


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
