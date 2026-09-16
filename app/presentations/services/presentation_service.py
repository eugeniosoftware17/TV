import copy

from django.db import transaction
from django.utils import timezone

from core.models import EventLog
from core.services import LoggingService
from presentations.models import MediaAsset, Presentation, Slide


class PresentationService:
    @staticmethod
    def create(*, name, description="", user=None, status=Presentation.Status.ACTIVE):
        presentation = Presentation.objects.create(
            name=name,
            description=description,
            status=status,
            created_by=user,
        )
        LoggingService.log(
            EventLog.EventType.PRESENTATION_CREATED,
            f"Presentación creada: {presentation.name}",
            user=user,
            presentation=presentation,
        )
        return presentation

    @staticmethod
    def update(presentation, *, name, description, status, user=None):
        presentation.name = name
        presentation.description = description
        presentation.status = status
        presentation.save()
        LoggingService.log(
            EventLog.EventType.PRESENTATION_UPDATED,
            f"Presentación modificada: {presentation.name}",
            user=user,
            presentation=presentation,
        )
        return presentation

    @staticmethod
    def delete(presentation, *, user=None):
        name = presentation.name
        presentation_id = presentation.pk
        presentation.delete()
        LoggingService.log(
            EventLog.EventType.PRESENTATION_DELETED,
            f"Presentación eliminada: {name}",
            user=user,
            metadata={"presentation_id": presentation_id},
        )

    @staticmethod
    @transaction.atomic
    def duplicate(presentation, *, user=None):
        new_presentation = Presentation.objects.create(
            name=f"{presentation.name} (copia)",
            description=presentation.description,
            status=Presentation.Status.INACTIVE,
            source_type=presentation.source_type,
            created_by=user,
        )

        slide_map = {}
        media_map = {}

        for media in presentation.media_assets.all():
            new_media = MediaAsset.objects.create(
                presentation=new_presentation,
                file=media.file,
                original_filename=media.original_filename,
                media_type=media.media_type,
                mime_type=media.mime_type,
                file_size=media.file_size,
                uploaded_by=user,
                is_processed=media.is_processed,
            )
            media_map[media.pk] = new_media

        for slide in presentation.slides.all():
            new_slide = Slide.objects.create(
                presentation=new_presentation,
                order=slide.order,
                slide_type=slide.slide_type,
                title=slide.title,
                subtitle=slide.subtitle,
                content=slide.content,
                duration=slide.duration,
                background_color=slide.background_color,
                background_image=media_map.get(slide.background_image_id),
                image=media_map.get(slide.image_id),
                video=media_map.get(slide.video_id),
                custom_content=copy.deepcopy(slide.custom_content),
            )
            slide_map[slide.pk] = new_slide

        LoggingService.log(
            EventLog.EventType.PRESENTATION_DUPLICATED,
            f"Presentación duplicada: {presentation.name} → {new_presentation.name}",
            user=user,
            presentation=new_presentation,
            metadata={"source_id": presentation.pk},
        )
        return new_presentation

    @staticmethod
    def toggle_status(presentation, *, user=None):
        if presentation.status == Presentation.Status.ACTIVE:
            presentation.status = Presentation.Status.INACTIVE
        else:
            presentation.status = Presentation.Status.ACTIVE
        presentation.save(update_fields=["status", "updated_at"])
        LoggingService.log(
            EventLog.EventType.PRESENTATION_TOGGLED,
            f"Estado cambiado a {presentation.get_status_display()}: {presentation.name}",
            user=user,
            presentation=presentation,
        )
        return presentation

    @staticmethod
    def get_by_token(token):
        return Presentation.objects.filter(token=token).first()

    @staticmethod
    def get_player_data(presentation):
        if not presentation.is_active:
            return None
        slides = [slide.to_player_dict() for slide in presentation.slides.all()]
        return {
            "id": presentation.pk,
            "name": presentation.name,
            "token": presentation.token,
            "updated_at": presentation.updated_at.isoformat(),
            "version": int(presentation.updated_at.timestamp()),
            "slides": slides,
        }

    @staticmethod
    def touch_updated(presentation):
        presentation.updated_at = timezone.now()
        presentation.save(update_fields=["updated_at"])
