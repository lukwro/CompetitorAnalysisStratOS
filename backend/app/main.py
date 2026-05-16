from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

MAX_COMPANY_NAME_LEN = 200


class CompanyIn(BaseModel):
    name: str


class CompanyOut(BaseModel):
    id: int
    name: str


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


def normalize_company_name(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Pole 'nazwa firmy' jest wymagane.")
    if len(normalized) > MAX_COMPANY_NAME_LEN:
        raise ValueError("Nazwa firmy może mieć maksymalnie 200 znaków.")
    return normalized


@app.post("/api/company", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyIn) -> CompanyOut:
    try:
        normalized_name = normalize_company_name(payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    companies.append(normalized_name)
    return CompanyOut(id=len(companies), name=normalized_name)


@app.get("/api/companies", response_model=list[CompanyOut])
def list_companies() -> list[CompanyOut]:
    return [CompanyOut(id=index + 1, name=name) for index, name in enumerate(companies)]


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
