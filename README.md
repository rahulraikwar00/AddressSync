# AddressSync

Update your address once. Every agency you consented to gets it automatically.

Most systems make you submit an address-change form to each bank, utility, and
office separately, then wait for each one to "approve" it. That's backwards.
Your address is *yours* — you should change it in one place, and agencies you
trust should subscribe to it.

This is a working prototype of that flip: **citizen-owned address + consent +
push-based sync**, built like India Stack's account aggregator / DigiLocker
consent model.

## How it works

```
                 ┌─────────────────────────────────────────────┐
                 │                  AddressSync                │
                 │                                             │
 citizen ───────►│  OTP login ──► one versioned address        │
 (Aadhaar)       │                    │                        │
                 │              update v1 ──► v2                │
 agency ◄────────│  pull API (needs active consent)             │
                 │                    ▲                        │
 agency ◄────────│  signed webhook ◄──┤                        │
                 │              outbox worker                  │
                 └─────────────────────────────────────────────┘
```

- The citizen has **one canonical address**; every change is a new version,
  old rows are never mutated (free audit trail).
- Consent is a first-class row per (citizen, agency): `granted` or `revoked`.
- Every state change writes an **event to an outbox table** in the same DB
  transaction. A background worker delivers those events as webhooks to each
  consented agency, **HMAC-SHA256 signed** so the agency can verify the sender.
- Agencies can also just **pull** the current address via
  `GET /agency/addresses/{consent_id}` — the API returns `403` the moment
  consent is revoked.
- Aadhaar is never stored raw: only a masked ref (`XXXX XXXX 1234`) and a hash
  for login lookup.

## Run it

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/uvicorn app.main:app --port 8000
```

Open **http://localhost:8000/demo** — a single page with the citizen panel on
the left, an agency panel in the middle, and the live sync feed on the right.
Demo credentials are prefilled automatically (Aadhaar `111122223333`; in dev
mode the OTP is shown on screen instead of being sent by SMS).

Docker instead: `./start.sh` from the repo root.

## Prove it without a browser

```bash
./demo.sh                  # replays the whole story with curl, step by step
cd backend && python smoke_test.py   # asserts every step end-to-end
```

The story it tells, in order:

1. Citizen logs in via OTP, updates their address (v2)
2. A new agency registers and points its webhook at the built-in fake inbox
3. Citizen grants consent → current address is pushed immediately
4. Citizen updates again → agency receives the change with no action needed
5. Citizen revokes → agency is notified, and its next pull returns 403

## API

| Method | Path | Who | What |
|---|---|---|---|
| POST | `/citizen/otp/request` | public | request login OTP |
| POST | `/citizen/otp/verify` | public | verify OTP → JWT |
| GET | `/citizen/me` | citizen | profile, current address, consents |
| PUT | `/citizen/address` | citizen | new address version (+ notify) |
| POST/DELETE | `/citizen/consents[...]` | citizen | grant / revoke agency access |
| POST | `/agencies/register` | public | create agency (API key shown once) |
| POST | `/agencies/login` | public | API key → JWT |
| PUT | `/agency/webhook` | agency | set push endpoint |
| GET | `/agency/addresses/{consent_id}` | agency | pull current address |

Interactive docs: `/docs`.

Webhooks agencies receive: `address.updated`, `consent.revoked` — JSON body
with `X-Signature: HMAC-SHA256(webhook_secret, body)` and `X-Event-Id`
headers. Failed deliveries retry 3 times with backoff, then mark as failed.

## Stack

FastAPI · SQLAlchemy · SQLite · PyJWT · httpx. One process: API + worker.

## What's simulated vs real

Simulated: the UIDAI layer (OTP is returned by the API in dev mode instead of
arriving via SMS) and the agencies themselves (the demo page hosts a fake
receiver so pushes have somewhere to land).

Real: consent lifecycle, address versioning, transactional outbox, HMAC-signed
delivery with retries, revocation propagation, JWT auth for both sides.

What production would add: actual UIDAI eKYC integration, Postgres, a real
job queue (Celery/SQS) instead of the in-process asyncio loop, Alembic
migrations, encrypted webhook secrets, rate limiting, and an audit-log UI.

## Deploy your own

Free public URL on Render (no credit card needed):

1. Push this repo to your GitHub account
2. [dashboard.render.com](https://dashboard.render.com) → **New → Web Service** → connect the repo
3. Render auto-detects the root `Dockerfile`. Instance type: **Free**
4. Add environment variables:
   - `WEBHOOK_BASE_URL` = `https://<your-service>.onrender.com` (so webhook pushes loop back correctly)
   - `SECRET_KEY` = any long random string
   - `DEV_MODE` = `true` (OTP shown on screen instead of SMS)
5. Set **Health Check Path** to `/health`, then deploy → open `https://<service>.onrender.com/demo`

Free-tier notes: sleeps after 15 min idle (~30–60s cold start on next visit);
the SQLite file resets on redeploy/restart, but `seed.py` reseeds on boot so
the demo always works — history just isn't permanent.

## License

MIT
