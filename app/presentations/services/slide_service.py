from django.db import transaction
from django.db.models import Max

from core.models import EventLog
from core.services import LoggingService
from presentations.models import Slide
from presentations.services.presentation_service import PresentationService


class SlideService:
    @staticmethod
    def _next_order(presentation):
        max_order = presentation.slides.aggregate(max_order=Max("order"))["max_order"]
        return (max_order or 0) + 1

    @staticmethod
    def create(presentation, *, slide_type=Slide.SlideType.TEXT, user=None, **fields):
        order = fields.pop("order", None)
        if order is None:
            order = SlideService._next_order(presentation)

        slide = Slide.objects.create(
            presentation=presentation,
            order=order,
            slide_type=slide_type,
            **fields,
        )
        PresentationService.touch_updated(presentation)
        LoggingService.log(
            EventLog.EventType.SLIDE_CREATED,
            f"Diapositiva creada en {presentation.name}: {slide}",
            user=user,
            presentation=presentation,
            metadata={"slide_id": slide.pk},
        )
        return slide

    @staticmethod
    def update(slide, *, user=None, **fields):
        for key, value in fields.items():
            setattr(slide, key, value)
        slide.save()
        PresentationService.touch_updated(slide.presentation)
        LoggingService.log(
            EventLog.EventType.SLIDE_UPDATED,
            f"Diapositiva modificada: {slide}",
            user=user,
            presentation=slide.presentation,
            metadata={"slide_id": slide.pk},
        )
        return slide

    @staticmethod
    def delete(slide, *, user=None):
        presentation = slide.presentation
        slide_label = str(slide)
        slide_id = slide.pk
        slide.delete()
        PresentationService.touch_updated(presentation)
        LoggingService.log(
            EventLog.EventType.SLIDE_DELETED,
            f"Diapositiva eliminada: {slide_label}",
            user=user,
            presentation=presentation,
            metadata={"slide_id": slide_id},
        )

    @staticmethod
    @transaction.atomic
    def duplicate(slide, *, user=None):
        new_order = SlideService._next_order(slide.presentation)
        new_slide = Slide.objects.create(
            presentation=slide.presentation,
            order=new_order,
            slide_type=slide.slide_type,
            title=f"{slide.title} (copia)" if slide.title else "",
            subtitle=slide.subtitle,
            content=slide.content,
            duration=slide.duration,
            background_color=slide.background_color,
            background_image=slide.background_image,
            image=slide.image,
            video=slide.video,
            custom_content=slide.custom_content,
        )
        PresentationService.touch_updated(slide.presentation)
        LoggingService.log(
            EventLog.EventType.SLIDE_CREATED,
            f"Diapositiva duplicada: {slide} → {new_slide}",
            user=user,
            presentation=slide.presentation,
            metadata={"source_slide_id": slide.pk, "slide_id": new_slide.pk},
        )
        return new_slide

    @staticmethod
    @transaction.atomic
    def reorder(presentation, slide_ids, *, user=None):
        for index, slide_id in enumerate(slide_ids):
            Slide.objects.filter(pk=slide_id, presentation=presentation).update(order=index)
        PresentationService.touch_updated(presentation)
        LoggingService.log(
            EventLog.EventType.SLIDE_REORDERED,
            f"Diapositivas reordenadas en {presentation.name}",
            user=user,
            presentation=presentation,
            metadata={"order": slide_ids},
        )
