from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import incidents, agents, chat, knowledge, dashboard, websocket, gemini
from app.database import engine, Base, SessionLocal
import app.models.user
import app.models.incident
import app.models.agent
import app.models.investigation
import app.models.knowledge
import app.models.escalation
import app.models.compliance
import app.models.metrics
import app.models.chat
import app.models.playbook

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed data on startup."""
    Base.metadata.create_all(bind=engine)
    print("[startup] Tables created.")

    # Seed demo data if DB is empty
    db = SessionLocal()
    try:
        from app.seed import seed_db
        seed_db(db)
    finally:
        db.close()

    yield  # app runs

app = FastAPI(
    title="Hausbank Autonomous Incident Resolution",
    description="Multi-agent AI system for automated ServiceNow incident handling",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routes
app.include_router(incidents.router,  prefix="/api/incidents",  tags=["Incidents"])
app.include_router(agents.router,     prefix="/api/agents",     tags=["Agents"])
app.include_router(chat.router,       prefix="/api/incidents",  tags=["Chat Room"])
app.include_router(knowledge.router,  prefix="/api/knowledge",  tags=["Knowledge"])
app.include_router(dashboard.router,  prefix="/api/dashboard",  tags=["Dashboard"])
app.include_router(gemini.router,     prefix="/api/gemini",     tags=["Gemini AI"])

# WebSocket — real-time chat events
app.include_router(websocket.router, tags=["WebSocket"])

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
