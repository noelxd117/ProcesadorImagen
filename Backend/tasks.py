from celery import Celery
from config import settings
import json

# Configurar Celery
celery = Celery(
    "procesador_imagenes",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuración
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
)

@celery.task(bind=True, name='tasks.procesar_imagen')
def procesar_imagen(self, task_id: str, original_path: str, output_path: str, 
                   process_type: str, parameters: str = None):
    """
    Tarea para procesar imagen
    
    Args:
        task_id: ID de la tarea
        original_path: Ruta del archivo original
        output_path: Ruta donde guardar el resultado
        process_type: Tipo de procesamiento (redimensionar, convertir, filtro, miniatura)
        parameters: JSON string con parámetros adicionales
    """
    from utils.image_processor import ImageProcessor
    from database import SessionLocal
    from models import Task, TaskStatus
    
    try:
        db = SessionLocal()
        
        # Actualizar estado a procesando
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PROCESSING
            db.commit()
        
        # Procesar imagen
        processor = ImageProcessor()
        params = json.loads(parameters) if parameters else {}
        
        result_path = processor.process(
            input_path=original_path,
            output_path=output_path,
            process_type=process_type,
            **params
        )
        
        # Actualizar a completada
        if task:
            task.status = TaskStatus.COMPLETED
            task.result_file_path = result_path
            db.commit()
        
        return {"status": "completada", "result_path": result_path}
        
    except Exception as e:
        # Actualizar a error
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.ERROR
            task.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=5, max_retries=3)
    
    finally:
        db.close()
