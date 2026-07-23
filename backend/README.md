# Hausbank Autonomous Incident Resolution

Multi-agent AI system for automated ServiceNow incident handling.

**Global Hausbank Hackathon — Operations & Efficiency Track**

---

## Quickstart (3 commands)

```bash
# 1. Start PostgreSQL with pgvector
docker compose up -d

# 2. Install dependencies and set up the database
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY in .env
alembic upgrade head
psql $DATABASE_URL -f seed/seed.sql

# 3. Run the server
python wsgi.py
```

API docs at: http://localhost:8000/docs

---

## Demo Scenarios

### Scenario 1 — False positive auto-closed
```bash
curl -X POST http://localhost:8000/api/incidents/2/triage
```
CPU spike that self-corrected. Incident lead agent classifies false (0.93 confidence), auto-closes.

### Scenario 2 — Self-healed
```bash
curl -X POST http://localhost:8000/api/incidents/1/triage
```
Disk full on Unix server. Healer agent matches log-cleanup playbook, executes, verifies, closes.

### Scenario 3 — Collaborative room
Trigger triage on an incident with no playbook match. Listener agent opens the chat room,
surfaces top 10 KB articles. User adds unix agent via the + button. Agent diagnoses live,
proposes fix with Approve/Decline. Knowledge agent drafts KB on resolution.

---

## Architecture

```
Incident Lead Agent  →  classifies real/false, routes
Healer Agent         →  matches playbook, executes via unix/windows agent
Listener Agent       →  opens chat room, surfaces top 10 articles (pgvector)
Unix Agent           →  executes playbooks OR diagnoses live in chat room
Windows Agent        →  same interface as unix (stub for now)
Knowledge Agent      →  drafts KB article from every resolution
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Claude API key — leave empty to run in mock mode |
| `HEALER_CONFIDENCE_THRESHOLD` | Min confidence for healer to act (default 0.85) |
| `SIMILARITY_TOP_K` | Articles shown in chat room (default 10) |
| `MAX_HOP_COUNT` | Max agent hops before hard escalation (default 3) |

---

## Project Structure

```
app/
  agents/      AI agent logic — each agent is one file
  core/        Shared: state object, guardrails, similarity search, WebSocket
  handlers/    Business logic called by routers
  models/      SQLAlchemy ORM — one file per table
  routers/     FastAPI routes — thin, calls handlers
  schemas/     Pydantic request/response models
alembic/       Database migrations
playbooks/     Healer agent playbook library (YAML)
seed/          Mock data SQL
```
