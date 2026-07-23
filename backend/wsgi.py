"""
Entry point.

Development:
    python wsgi.py

Production (gunicorn + uvicorn workers):
    gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker
"""
import uvicorn
from app.main import app  # noqa: F401 — needed for gunicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
