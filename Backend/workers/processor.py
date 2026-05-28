"""
Worker Celery para procesar imágenes
Ejecutar con: celery -A workers.processor worker --loglevel=info
"""

from tasks import celery
import logging

logger = logging.getLogger(__name__)

# Las tareas se definen en tasks.py
# Este archivo puede servir para configuración adicional del worker
