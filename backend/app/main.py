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
REJESTR_IO_TIMEOUT_SECONDS = float(os.getenv("REJESTR_IO_TIMEOUT_SECONDS", "10"))


class CompanyIn(BaseModel):
    nip: str


class CompanyOut(BaseModel):
    id: int
    nip: str
    organization_name: str | None = None
    organization_status: str | None = None
    city: str | None = None
    address: str | None = None
    krd_status: str | None = None


app = FastAPI(title="CompetitorAnalysisStratOS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TASK-1/TASK-2: in-memory store. DB integration is planned in next tasks.
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


def map_rejestr_payload(payload: dict, nip: str) -> dict:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Nieprawidłowy format odpowiedzi z rejestr.io.")

    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Nieprawidłowy format danych organizacji z rejestr.io.")

    return {
        "nip": nip,
        "organization_name": data.get("nazwa") or data.get("nazwa_pelna") or data.get("name"),
        "organization_status": data.get("status") or data.get("status_podmiotu"),
        "city": data.get("miasto") or data.get("miejscowosc") or data.get("city"),
        "address": data.get("adres") or data.get("ulica") or data.get("address"),
        "krd_status": data.get("krd") or data.get("krd_status") or data.get("status_krd"),
    }


def fetch_rejestr_data(nip: str) -> dict:
    if not REJESTR_IO_API_KEY:
        raise HTTPException(status_code=500, detail="Brak konfiguracji REJESTR_IO_API_KEY.")

    url = f"{REJESTR_IO_BASE_URL.rstrip('/')}/org/nip{nip}"
    headers = {
        "X-API-KEY": REJESTR_IO_API_KEY,
    }

    try:
        with httpx.Client(timeout=REJESTR_IO_TIMEOUT_SECONDS) as client:
            response = client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Timeout podczas łączenia z rejestr.io.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Błąd połączenia z rejestr.io.") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Nie znaleziono danych organizacji dla podanego NIP.")
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

    return map_rejestr_payload(payload, nip)


@app.post("/api/company", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyIn) -> CompanyOut:
    try:
        normalized_nip = normalize_nip(payload.nip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    company_data = fetch_rejestr_data(normalized_nip)
    company = CompanyOut(id=len(companies) + 1, **company_data)
    companies.append(company)
    return company


@app.get("/api/companies", response_model=list[CompanyOut])
def list_companies() -> list[CompanyOut]:
    return companies


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
