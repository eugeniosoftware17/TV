"""
Orquestación de importación PowerPoint → Presentation + Slides.

Preparado para ejecutarse en hilo (actual) o cola Celery/RQ (futuro).
"""
import logging
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from core.models import EventLog
from core.services import LoggingService
from presentations.models import MediaAsset, PowerPointImport, Presentation, Slide
from presentations.services.powerpoint_converter import PowerPointConversionError, PowerPointConverter
from presentations.services.powerpoint_metadata import PowerPointMetadataError, extract_pptx_metadata
from presentations.services.presentation_service import PresentationService

logger = logging.getLogger(__name__)


class PowerPointImportService:
    @staticmethod
    def start_import(*, uploaded_file, user=None, name=None):
        """
        Crea Presentation + PowerPointImport y encola el procesamiento.
        Retorna el registro PowerPointImport.
        """
        from presentations.tasks.powerpoint_tasks import enqueue_powerpoint_import

        original_filename = uploaded_file.name
        presentation_name = name or Path(original_filename).stem

        presentation = Presentation.objects.create(
            name=presentation_name,
            description=f"Importada desde PowerPoint: {original_filename}",
            status=Presentation.Status.INACTIVE,
            source_type=Presentation.SourceType.POWERPOINT,
            created_by=user,
        )

        ppt_import = PowerPointImport.objects.create(
            presentation=presentation,
            original_file=uploaded_file,
            original_filename=original_filename,
            status=PowerPointImport.Status.PENDING,
            created_by=user,
        )

        enqueue_powerpoint_import(ppt_import.pk)
        return ppt_import

    @staticmethod
    def process(import_id: int):
        """Procesa una importación PowerPoint (punto de entrada para tareas)."""
        try:
            ppt_import = PowerPointImport.objects.select_related("presentation").get(pk=import_id)
        except PowerPointImport.DoesNotExist:
            logger.error("PowerPointImport %s no encontrado", import_id)
            return

        PowerPointImportService._run_processing(ppt_import)

    @staticmethod
    def _run_processing(ppt_import: PowerPointImport):
        presentation = ppt_import.presentation
        ppt_import.status = PowerPointImport.Status.PROCESSING
        ppt_import.error_message = ""
        ppt_import.save(update_fields=["status", "error_message"])

        work_dir = None
        try:
            original_path = Path(ppt_import.original_file.path)
            extension = original_path.suffix.lower()

            slides_meta = []
            if extension == ".pptx":
                meta = extract_pptx_metadata(original_path)
                slides_meta = meta["slides"]
                ppt_import.slide_count = meta["slide_count"]
                ppt_import.save(update_fields=["slide_count"])

            work_dir = tempfile.mkdtemp(prefix="cloudscreen_ppt_")
            work_path = Path(work_dir)

            converter = PowerPointConverter(
                libreoffice_path=getattr(settings, "LIBREOFFICE_BINARY", None),
                dpi=getattr(settings, "POWERPOINT_RENDER_DPI", 150),
                timeout=getattr(settings, "POWERPOINT_CONVERSION_TIMEOUT", 300),
            )
            image_paths = converter.convert_to_slide_images(original_path, work_path)

            if extension == ".pptx" and slides_meta and len(image_paths) != len(slides_meta):
                logger.warning(
                    "Diapositivas PPTX (%s) vs imágenes (%s) no coinciden; se usa conteo de imágenes.",
                    len(slides_meta),
                    len(image_paths),
                )

            if not slides_meta:
                ppt_import.slide_count = len(image_paths)
                ppt_import.save(update_fields=["slide_count"])

            PowerPointImportService._create_slides_from_images(
                presentation=presentation,
                image_paths=image_paths,
                slides_meta=slides_meta,
                ppt_import=ppt_import,
                user=ppt_import.created_by,
            )

            ppt_import.status = PowerPointImport.Status.COMPLETED
            ppt_import.processed_slide_count = len(image_paths)
            ppt_import.processed_at = timezone.now()
            ppt_import.save(update_fields=["status", "processed_slide_count", "processed_at"])

            PresentationService.touch_updated(presentation)

            LoggingService.log(
                EventLog.EventType.PRESENTATION_IMPORTED,
                f"Presentación importada desde PowerPoint: {presentation.name} ({len(image_paths)} diapositivas)",
                user=ppt_import.created_by,
                presentation=presentation,
                metadata={
                    "import_id": ppt_import.pk,
                    "original_filename": ppt_import.original_filename,
                    "slide_count": len(image_paths),
                },
            )

        except (PowerPointConversionError, PowerPointMetadataError) as exc:
            PowerPointImportService._mark_failed(ppt_import, str(exc))
        except Exception as exc:
            logger.exception("Error inesperado importando PowerPoint %s", ppt_import.pk)
            PowerPointImportService._mark_failed(
                ppt_import,
                "No fue posible procesar este archivo PowerPoint.",
            )
        finally:
            if work_dir:
                shutil.rmtree(work_dir, ignore_errors=True)

    @staticmethod
    @transaction.atomic
    def _create_slides_from_images(*, presentation, image_paths, slides_meta, ppt_import, user):
        default_duration = getattr(settings, "POWERPOINT_DEFAULT_SLIDE_DURATION", 10)

        for index, image_path in enumerate(image_paths):
            ppt_import.processed_slide_count = index + 1
            ppt_import.save(update_fields=["processed_slide_count"])

            title = ""
            if index < len(slides_meta):
                title = slides_meta[index].get("title", "")
            if not title:
                title = f"Diapositiva {index + 1}"

            png_bytes = image_path.read_bytes()
            rel_path = f"presentations/{presentation.pk}/processed/slides/{index + 1:03d}.png"
            saved_path = default_storage.save(rel_path, ContentFile(png_bytes))

            media = MediaAsset.objects.create(
                presentation=presentation,
                file=saved_path,
                original_filename=f"{index + 1:03d}.png",
                media_type=MediaAsset.MediaType.IMAGE,
                mime_type="image/png",
                file_size=len(png_bytes),
                uploaded_by=user,
                is_processed=True,
            )

            Slide.objects.create(
                presentation=presentation,
                order=index,
                slide_type=Slide.SlideType.IMAGE,
                title=title,
                duration=default_duration,
                background_color="#000000",
                image=media,
                custom_content={
                    "imported_from": "powerpoint",
                    "import_id": ppt_import.pk,
                    "source_slide_index": index + 1,
                },
            )

    @staticmethod
    def _mark_failed(ppt_import: PowerPointImport, message: str):
        ppt_import.status = PowerPointImport.Status.FAILED
        ppt_import.error_message = message
        ppt_import.processed_at = timezone.now()
        ppt_import.save(update_fields=["status", "error_message", "processed_at"])

        LoggingService.log(
            EventLog.EventType.PRESENTATION_IMPORT_FAILED,
            f"Error al importar PowerPoint: {ppt_import.original_filename} — {message}",
            user=ppt_import.created_by,
            presentation=ppt_import.presentation,
            metadata={"import_id": ppt_import.pk},
        )

    @staticmethod
    def get_status_payload(ppt_import: PowerPointImport) -> dict:
        total = ppt_import.slide_count or ppt_import.processed_slide_count or 0
        return {
            "id": ppt_import.pk,
            "status": ppt_import.status,
            "status_label": ppt_import.get_status_display(),
            "slide_count": total,
            "processed_slide_count": ppt_import.processed_slide_count,
            "error_message": ppt_import.error_message,
            "presentation_id": ppt_import.presentation_id,
            "presentation_name": ppt_import.presentation.name,
            "editor_url": ppt_import.presentation.get_absolute_url() if ppt_import.status == PowerPointImport.Status.COMPLETED else None,
        }
