"""
Tareas de procesamiento PowerPoint.

Actualmente usa threading. Para Celery/RQ, reemplazar enqueue_powerpoint_import
y registrar process_powerpoint_import como tarea.
"""
import logging
import threading

from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)


def process_powerpoint_import(import_id: int):
    """Punto de entrada único para procesamiento (thread, Celery o RQ)."""
    from presentations.services.powerpoint_import_service import PowerPointImportService

    PowerPointImportService.process(import_id)


def _run_in_thread(import_id: int):
    try:
        process_powerpoint_import(import_id)
    finally:
        connection.close()


def enqueue_powerpoint_import(import_id: int):
    """
    Encola procesamiento en segundo plano.

    Futuro (Celery):
        from presentations.tasks.powerpoint_tasks import process_powerpoint_import
        process_powerpoint_import.delay(import_id)
    """
    if getattr(settings, "POWERPOINT_USE_CELERY", False):
        raise NotImplementedError("Celery no está configurado aún. Use POWERPOINT_USE_CELERY=False.")

    thread = threading.Thread(
        target=_run_in_thread,
        args=(import_id,),
        name=f"ppt-import-{import_id}",
        daemon=True,
    )
    thread.start()
    logger.info("Importación PowerPoint %s encolada en hilo de fondo", import_id)
