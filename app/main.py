import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.config import UPLOAD_DIR
from app.database import init_db
from app.auth import initialize_auth
from app.templating import render_template
from app.routers import (
    auth_routes,
    dashboard_routes,
    interior_routes,
    party_routes,
    jewelry_routes,
    api_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    initialize_auth()
    yield

app = FastAPI(
    title="PocketSmart AI",
    description="Budget-based AI recommendations for Home Interior Planning, Party Planning, and Jewelry Selection with Outfit-Image Analysis",
    version="1.0.0",
    lifespan=lifespan
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Mount static files and uploads
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include Routers
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(interior_routes.router)
app.include_router(party_routes.router)
app.include_router(jewelry_routes.router)
app.include_router(api_routes.router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return render_template(request, "base.html", {
        "user": None,
        "content_override": """
        <div class="max-w-xl mx-auto text-center py-20">
            <div class="text-6xl mb-4">🔍</div>
            <h1 class="text-3xl font-bold text-slate-800 dark:text-white mb-2">Page Not Found</h1>
            <p class="text-slate-600 dark:text-slate-400 mb-6">The page or plan you are looking for does not exist or has been moved.</p>
            <a href="/" class="btn-primary">Return to Home</a>
        </div>
        """
    }, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
