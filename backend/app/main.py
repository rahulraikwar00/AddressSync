import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .db import Base, engine
from .events import worker_loop
from .routes import agency, citizen, demo

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

STATIC_DIR = Path(__file__).parent / "static"

DESCRIPTION = """
Consent-based address sync prototype (India Stack style).

* Citizens own **one versioned address** and grant/revoke per-agency consent.
* Address changes are written to a transactional **outbox** and delivered as
  HMAC-signed webhooks by a background worker (with retries).
* Agencies pull via `GET /agency/addresses/{consent_id}` — requires active consent.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    worker = asyncio.create_task(worker_loop())
    yield
    worker.cancel()


app = FastAPI(
    title="AddressSync",
    version="2.0.0",
    description=DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(citizen.router)
app.include_router(agency.router)
app.include_router(demo.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/demo")


@app.get("/demo", include_in_schema=False)
def demo_page():
    return FileResponse(STATIC_DIR / "demo.html")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "AddressSync", "version": "2.0.0"}
