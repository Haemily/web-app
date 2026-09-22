# Haemily

Haemily is a **synthetic community app prototype** based on the original HTML/CSS mockup in this repository. The frontend uses React, TypeScript, and Vite. The API uses FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

This is a software demo, not an HSS service or a source of medical guidance. Use synthetic information only. The seeded people, posts, events, and activities are fictional examples.

## What works

- Demo sign-in with a seeded member or moderator account; server-side sessions and sign-out.
- Home feed, text search, format/source filters, topic/life-stage browsing, content detail, saved posts, reactions, comments, replies, and post creation.
- Event registration/cancellation; community activity creation, joining, and leaving.
- Community group descriptions and a privacy explanation before any group access. **This demo does not create group membership or open WhatsApp.**
- Non-medical practical-help requests, volunteer offers, requester acceptance/cancellation, and concern reporting.
- Moderator-only report queue with review status changes.

The original `app.js` is retained as a design and interaction reference. Vite runs `frontend/src/main.tsx`; the old script is not loaded.

## Prerequisites

- Node.js 20+ and npm
- Python 3.10+ and `uv` or `pip`
- PostgreSQL 17, or Colima/Docker with `docker-compose`

## Local setup

From the repository root:

```bash
# If using Colima on macOS:
colima start
docker-compose up -d --wait
# On systems with the Docker Compose plugin, use: docker compose up -d --wait

npm install
uv venv .venv
uv pip install --python .venv/bin/python -r backend/requirements.txt

cd backend
../.venv/bin/alembic upgrade head
DEMO_PASSWORD=haemily-demo-2026 ../.venv/bin/python -m app.seed
../.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `uv` is unavailable, replace the two `uv` commands with `python3 -m venv .venv` and `.venv/bin/python -m pip install -r backend/requirements.txt`.

In a second terminal at the repository root:

```bash
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to FastAPI on port 8000. Sign in as `SunlitKoi`, `BrightKite`, or `HSSModerator` with the value you set in `DEMO_PASSWORD`. The password above is for a disposable local demo only; set your own 12+ character value for any shared development environment. Seeding is idempotent and requires `DEMO_PASSWORD`.

To connect to another PostgreSQL instance, set `DATABASE_URL` for migration, seed, and server, for example `postgresql+psycopg://user:password@localhost:5432/haemily`. The compose file binds the local demo database to `127.0.0.1:5432` and uses demo-only credentials.

## Verification

```bash
npm run build
cd backend
../.venv/bin/python -m pytest -q
../.venv/bin/alembic current
# With Vite and FastAPI running and PostgreSQL seeded:
DEMO_PASSWORD=haemily-demo-2026 ../.venv/bin/python tests/e2e_http.py
```

The backend test suite uses an isolated SQLite database for quick behavior tests. It covers authentication/CSRF, post creation and soft deletion, comments/replies, saves/reactions, contact-detail validation, event registration, activities, practical help, ownership checks, and moderator access. The HTTP flow script sends requests through Vite's `/api` proxy into FastAPI and PostgreSQL. It creates and then soft-deletes synthetic records; it leaves a synthetic review report in the local database. No browser is required for this check.

## API contract

All application endpoints live under `/api`. Interactive documentation is at `http://127.0.0.1:8000/api/docs`. JSON request bodies are required for writes with a body. Errors use FastAPI's `{ "detail": ... }` shape. All endpoints except `/api/health` and `/api/auth/login` require a session.

`POST /api/auth/login` accepts `{ "username": string, "password": string }`. It sets an HTTP-only session cookie and returns `{ "user": { "id", "username", "role" }, "csrf_token": string }`. `GET /api/auth/session` returns the same shape; `POST /api/auth/logout` ends the session. Every authenticated mutation also requires `X-CSRF-Token` with the returned token. Login failures are throttled locally.

| Area | Endpoints | Main body / response |
|---|---|---|
| Content | `GET/POST /content`, `GET/DELETE /content/{id}` | Create: `title`, `body`, `format` (`Question`, `Story`, `Discussion`), `topic`, `stage`. Read includes author username, verification flag, counts, and current user's saved/reacted flags. |
| Saved/reactions | `PUT/DELETE /content/{id}/save`, `PUT/DELETE /content/{id}/reaction` | Idempotent per user; success is `204`. |
| Comments | `GET/POST /content/{id}/comments`, `DELETE /comments/{id}`, `GET /me/comments` | Create: `body`, optional `parent_id` for a reply. |
| Events | `GET /events`, `PUT/DELETE /events/{id}/registration` | Event includes title, time, mode, host, and current user's registered flag. |
| Activities | `GET/POST /activities`, `DELETE /activities/{id}`, `PUT/DELETE /activities/{id}/join` | Create: `title`, `description`, `kind` (`Meetup` or `Open jio`), future ISO `starts_at`, `location`. |
| Groups | `GET /groups` | Descriptions only; no external links or membership action. |
| Practical help | `GET/POST /help-requests`, `GET/DELETE /help-requests/{id}`, `POST /help-requests/{id}/cancel`, `POST /help-requests/{id}/offers`, `DELETE /help-requests/{id}/offers/mine`, `POST /help-requests/{id}/offers/{offer_id}/accept` | Create: `title`, `description`, general `area`, `non_medical_acknowledged: true`. Offers are visible only to the requester. Connected requests are visible only to involved members and moderators. |
| Reports | `POST/GET /reports`, `PATCH /reports/{id}` | Create: `target_type` (`content`, `activity`, `help_request`), `target_id`, `reason` (`unsafe`, `medical`, `privacy`, `other`), optional `details`. List and status updates require moderator role. |

Responses for created records return `201`; missing items return `404`; unauthorized access returns `401` or `403`; invalid input returns `422`; invalid state transitions return `409`. Times are stored as timezone-aware UTC timestamps and rendered in the viewer's local timezone.

## Data model and privacy

`User` owns content, comments, activities, and help requests. Join tables (`Save`, `Reaction`, `Registration`, `ActivityJoin`) use composite keys so an action can happen once per member/item. `Session` stores a hash of a random session token, not the raw cookie value. `Report` stores a moderation concern and status. `CommunityGroup` contains only public descriptions.

The API does not collect phone numbers, diagnoses, treatment records, or real patient identities. Public text rejects email addresses and common Singapore mobile-number patterns; that is a basic guard, **not** a complete sensitive-data detector. UI copy asks members to avoid identifiable information. Passwords are Argon2-hashed. Cookies are HTTP-only and SameSite=Lax, become Secure when `APP_ENV=production`, and mutations require a CSRF token. Ownership and moderator permissions are enforced on the server. Request bodies are not logged by the app.

`Content`, `Comment`, `Activity`, and `HelpRequest` have `deleted_at` for soft deletion. Ordinary reads hide soft-deleted records; a separate retention and erasure process would be required for real patient-data handling, including backups. Sessions and membership-style join rows are hard-deleted when removed. This prototype has no real identity proofing, clinical review workflow, audit log, persistent distributed rate limiter, or production data-retention policy, so it must not be deployed for real patient use.

## Remaining prototype gaps

- The original mockup's WhatsApp handoff and group joining are represented by an informational privacy dialog. There are no real group links or memberships.
- AMA guest questions, recordings, AI summaries, notification preferences, and the broader moderator publishing/policy tools from the mockup are not connected to services in this version.
- Practical-help acceptance changes status but does not reveal contact details or send messages. A real service would need verified identity, consent, safeguarding, and an audited contact workflow.
- The HTTP flow check covers the main API interactions through the Vite proxy. A full automated browser test and mobile visual regression suite are not included.

## Repository layout

```text
frontend/src/       React components, API client, types, responsive additions
styles.css          Original visual design system
backend/app/        FastAPI, SQLAlchemy models, validation, synthetic seed
backend/alembic/    PostgreSQL migration
backend/tests/      API behavior tests
compose.yaml        Local PostgreSQL
app.js              Original mockup reference; not loaded by Vite
```
