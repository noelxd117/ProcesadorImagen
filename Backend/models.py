from sqlalchemy import Column, String, Integer, DateTime, Enum, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    """Estados posibles de una tarea"""
    PENDING = "pendiente"
    PROCESSING = "en_proceso"
    COMPLETED = "completada"
    ERROR = "error"

class ProcessType(str, enum.Enum):
    """Tipos de procesamiento disponibles"""
    RESIZE = "redimensionar"
    CONVERT = "convertir"
    FILTER = "filtro"
    THUMBNAIL = "miniatura"

class Task(Base):
    """Modelo de tarea de procesamiento"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    process_type = Column(Enum(ProcessType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    
    # Parámetros de procesamiento (JSON string)
    parameters = Column(Text, nullable=True)
    
    # URLs
    original_file_path = Column(String(500), nullable=True)
    result_file_path = Column(String(500), nullable=True)
    
    # Metadata
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task {self.id} - {self.status.value}>"
