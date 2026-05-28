from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# Configuración
from config import settings

# Crear carpetas necesarias
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.RESULTS_FOLDER, exist_ok=True)

# IMPORTANTE:
# importar modelos antes de crear tablas
import models

from database import create_tables

# Crear tablas
create_tables()

# Importar rutas
from routes import upload, status, results


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación")
    yield
    print("Cerrando aplicación")


# Crear app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas API
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(status.router, prefix="/api/status", tags=["status"])
app.include_router(results.router, prefix="/api/results", tags=["results"])


@app.get("/api")
async def api_root():
    return {
        "nombre": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "activo"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Servir frontend
frontend_path = "/frontend"

if os.path.exists(frontend_path):
    app.mount(
        "/",
        StaticFiles(directory=frontend_path, html=True),
        name="frontend"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )