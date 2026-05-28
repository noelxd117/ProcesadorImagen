from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Task, TaskStatus, ProcessType
from schemas import UploadResponse, TaskResponse
from tasks import procesar_imagen
import uuid
import os
from config import settings
import shutil

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    process_type: ProcessType = Form(...),
    parameters: str = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Subir imagen y crear tarea de procesamiento
    
    - **file**: Archivo de imagen
    - **process_type**: Tipo de procesamiento (redimensionar, convertir, filtro, miniatura)
    - **parameters**: JSON string con parámetros (opcional)
    """
    
    # Validar tipo de archivo
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    # Validar tamaño
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")
    
    # Crear directorio si no existe
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    # Generar ID de tarea
    task_id = str(uuid.uuid4())
    
    # Guardar archivo original
    file_ext = os.path.splitext(file.filename)[1]
    original_path = os.path.join(settings.UPLOAD_FOLDER, f"{task_id}_original{file_ext}")
    
    with open(original_path, "wb") as f:
        f.write(contents)
    
    # Crear tarea en BD
    task = Task(
        id=task_id,
        original_filename=file.filename,
        process_type=process_type,
        status=TaskStatus.PENDING,
        parameters=parameters,
        original_file_path=original_path
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Crear ruta de salida
    output_path = os.path.join(settings.RESULTS_FOLDER, f"{task_id}_result")
    os.makedirs(settings.RESULTS_FOLDER, exist_ok=True)
    
    # Enviar tarea a cola
    procesar_imagen.delay(
        task_id=task_id,
        original_path=original_path,
        output_path=output_path,
        process_type=process_type.value,
        parameters=parameters
    )
    
    return UploadResponse(
        task_id=task_id,
        status="pendiente",
        message=f"Tarea {task_id} creada. Procesando..."
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_upload_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Obtener estado de una tarea específica"""
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return task
