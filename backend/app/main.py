from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

NIP_LENGTH = 10


class CompanyIn(BaseModel):
    nip: str


class CompanyOut(BaseModel):
    id: int
    nip: str


app = FastAPI(title="CompetitorAnalysisStratOS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TASK-1: in-memory store. DB integration is planned in next tasks.
companies: list[str] = []
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


@app.post("/api/company", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyIn) -> CompanyOut:
    try:
        normalized_nip = normalize_nip(payload.nip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    companies.append(normalized_nip)
    return CompanyOut(id=len(companies), nip=normalized_nip)


@app.get("/api/companies", response_model=list[CompanyOut])
def list_companies() -> list[CompanyOut]:
    return [CompanyOut(id=index + 1, nip=nip) for index, nip in enumerate(companies)]


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
