import mimetypes

from core.models import EventLog
from core.services import LoggingService
from presentations.models import MediaAsset
from presentations.validators import detect_media_type, validate_media_file


class MediaService:
    @staticmethod
    def upload(presentation, uploaded_file, *, user=None):
        validate_media_file(uploaded_file)
        media_type = detect_media_type(uploaded_file.name)
        mime_type = uploaded_file.content_type or mimetypes.guess_type(uploaded_file.name)[0] or ""

        media = MediaAsset.objects.create(
            presentation=presentation,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            media_type=media_type,
            mime_type=mime_type,
            file_size=uploaded_file.size,
            uploaded_by=user,
        )
        LoggingService.log(
            EventLog.EventType.PRESENTATION_UPDATED,
            f"Archivo subido: {media.original_filename}",
            user=user,
            presentation=presentation,
            metadata={"media_id": media.pk},
        )
        return media
