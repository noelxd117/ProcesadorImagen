from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Task, TaskStatus
import os

router = APIRouter()

@router.get("/{task_id}")
async def download_result(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Descargar imagen procesada
    
    Solo disponible si el estado es "completada"
    """
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Tarea aún no completada. Estado: {task.status.value}"
        )
    
    if not task.result_file_path or not os.path.exists(task.result_file_path):
        raise HTTPException(status_code=404, detail="Archivo de resultado no encontrado")
    
    return FileResponse(
        path=task.result_file_path,
        filename = os.path.basename(task.result_file_path),
        media_type="application/octet-stream"
    )

@router.get("/{task_id}/info")
async def get_result_info(
    task_id: str,
    db: Session = Depends(get_db)
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada"
        )

    return {
        "task_id": task.id,
        "original_filename": task.original_filename,
        "process_type": str(task.process_type),
        "status": str(task.status),
        "result_available": task.status == TaskStatus.COMPLETED,
        "result_file_path": task.result_file_path,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }