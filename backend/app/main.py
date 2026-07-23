from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import incidents, agents, chat, knowledge, dashboard, websocket

app = FastAPI(
    title="Hausbank Autonomous Incident Resolution",
    description="Multi-agent AI system for automated ServiceNow incident handling",
    version="1.0.0",
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

# WebSocket — real-time chat events
app.include_router(websocket.router, tags=["WebSocket"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
