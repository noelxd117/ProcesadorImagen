from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # API
    API_TITLE: str = "Procesador de Imágenes"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/procesador_db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
    
    # Almacenamiento
    UPLOAD_FOLDER: str = "/tmp/uploads"
    RESULTS_FOLDER: str = "/tmp/results"
    
    # Tamaño máximo de archivo (10MB)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
