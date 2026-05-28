from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Task
from schemas import TaskResponse
import asyncio
import json

router = APIRouter()

@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Obtener estado actual de una tarea"""
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return {
        "id": task.id,
        "status": task.status.value,
        "progress": 100 if task.status.value == "completada" else 0
    }

async def generate_sse_stream(task_id: str):
    """Generador para SSE - enviar actualizaciones de estado"""
    from database import SessionLocal
    
    last_status = None
    max_attempts = 600  # 10 minutos máximo
    attempt = 0
    
    while attempt < max_attempts:
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                yield f"data: {json.dumps({'error': 'Tarea no encontrada'})}\n\n"
                break
            
            # Enviar si el estado cambió
            if last_status != task.status.value:
                data = {
                    "task_id": task.id,
                    "status": task.status.value,
                    "result_file_path": task.result_file_path,
                    "error_message": task.error_message
                }
                yield f"data: {json.dumps(data)}\n\n"
                last_status = task.status.value
                
                # Terminar cuando se complete o falle
                if task.status.value in ["completada", "error"]:
                    break
            
            # Esperar 1 segundo antes de siguiente check
            await asyncio.sleep(1)
            attempt += 1
        finally:
            db.close()

@router.get("/{task_id}/stream")
async def stream_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Stream SSE del estado de una tarea
    
    Estados: pendiente -> en_proceso -> completada (o error)
    """
    
    # Verificar que la tarea existe
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return StreamingResponse(
        generate_sse_stream(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
