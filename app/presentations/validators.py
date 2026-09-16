import os
import zipfile

from django.conf import settings
from django.core.exceptions import ValidationError


def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()


def validate_media_file(uploaded_file):
    ext = get_file_extension(uploaded_file.name)
    if ext not in settings.ALLOWED_MEDIA_EXTENSIONS:
        raise ValidationError(
            f"Formato no permitido. Extensiones válidas: "
            f"{', '.join(sorted(settings.ALLOWED_MEDIA_EXTENSIONS))}"
        )

    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if uploaded_file.size > max_size:
        raise ValidationError(f"El archivo excede el tamaño máximo de {max_size // (1024 * 1024)} MB.")


def detect_media_type(filename):
    ext = get_file_extension(filename)
    if ext in settings.ALLOWED_IMAGE_EXTENSIONS:
        return "image"
    if ext in settings.ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    if ext in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        return "document"
    return "document"


POWERPOINT_MIME_TYPES = {
    ".pptx": {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/octet-stream",
        "application/zip",
    },
    ".ppt": {
        "application/vnd.ms-powerpoint",
        "application/octet-stream",
    },
}


def validate_powerpoint_file(uploaded_file):
    """Valida extensión, tamaño, MIME y estructura básica de PowerPoint."""
    ext = get_file_extension(uploaded_file.name)
    allowed = getattr(settings, "ALLOWED_POWERPOINT_EXTENSIONS", {".pptx", ".ppt"})

    if ext not in allowed:
        raise ValidationError(
            f"Formato no permitido. Use: {', '.join(sorted(allowed))}"
        )

    max_size = getattr(settings, "POWERPOINT_MAX_FILE_SIZE", 100 * 1024 * 1024)
    if uploaded_file.size > max_size:
        raise ValidationError(
            f"El archivo excede el tamaño máximo de {max_size // (1024 * 1024)} MB."
        )

    if uploaded_file.size == 0:
        raise ValidationError("El archivo está vacío.")

    content_type = (uploaded_file.content_type or "").lower()
    allowed_mimes = POWERPOINT_MIME_TYPES.get(ext, set())
    if content_type and allowed_mimes and content_type not in allowed_mimes:
        raise ValidationError("El tipo MIME del archivo no corresponde a un PowerPoint válido.")

    if ext == ".pptx":
        _validate_pptx_structure(uploaded_file)

    uploaded_file.seek(0)


def _validate_pptx_structure(uploaded_file):
    """Verifica que .pptx sea un ZIP válido con estructura Office Open XML."""
    try:
        uploaded_file.seek(0)
        if not zipfile.is_zipfile(uploaded_file):
            raise ValidationError("El archivo .pptx está corrupto o no es válido.")
        with zipfile.ZipFile(uploaded_file) as archive:
            names = archive.namelist()
            if not any(name.startswith("ppt/") for name in names):
                raise ValidationError("El archivo no contiene una presentación PowerPoint válida.")
    except zipfile.BadZipFile as exc:
        raise ValidationError("El archivo .pptx está corrupto.") from exc
    finally:
        uploaded_file.seek(0)
