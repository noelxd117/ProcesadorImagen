from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import TaskStatus, ProcessType
import json

class TaskBase(BaseModel):
    """Schema base de tarea"""
    original_filename: str
    process_type: ProcessType
    parameters: Optional[str] = None

class TaskCreate(TaskBase):
    """Schema para crear tarea"""
    pass

class TaskResponse(TaskBase):
    """Schema de respuesta de tarea"""
    id: str
    status: TaskStatus
    original_file_path: Optional[str] = None
    result_file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    """Schema para actualizar estado de tarea"""
    status: TaskStatus
    result_file_path: Optional[str] = None
    error_message: Optional[str] = None

class ProcessRequest(BaseModel):
    """Schema para solicitud de procesamiento"""
    process_type: ProcessType = Field(..., description="Tipo de procesamiento")
    parameters: Optional[dict] = Field(default=None, description="Parámetros específicos del procesamiento")

class UploadResponse(BaseModel):
    """Schema de respuesta al subir archivo"""
    task_id: str
    status: str = "pendiente"
    message: str
