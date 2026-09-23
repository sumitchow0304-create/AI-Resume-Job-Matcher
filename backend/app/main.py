from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .config import settings
from .routers import auth, jobs, resumes, analysis

Base.metadata.create_all(bind=engine)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(analysis.router)

FRONTEND = Path(settings.FRONTEND_DIR) if settings.FRONTEND_DIR else Path(__file__).resolve().parents[2] / "frontend"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")

app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
