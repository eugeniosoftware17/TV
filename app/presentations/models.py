import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def generate_presentation_token():
    return secrets.token_urlsafe(16)


def media_upload_path(instance, filename):
    safe_name = slugify(filename.rsplit(".", 1)[0]) or "file"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    folder = "presentations/media"
    if instance.presentation_id:
        folder = f"presentations/{instance.presentation_id}/media"
    return f"{folder}/{safe_name}.{ext}"


def powerpoint_original_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pptx"
    safe_name = slugify(filename.rsplit(".", 1)[0]) or "presentation"
    presentation_id = instance.presentation_id or "pending"
    return f"presentations/{presentation_id}/original/{safe_name}.{ext}"


class Presentation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Activa"
        INACTIVE = "inactive", "Inactiva"

    class SourceType(models.TextChoices):
        MANUAL = "manual", "Manual"
        POWERPOINT = "powerpoint", "PowerPoint"

    name = models.CharField("Nombre", max_length=200)
    description = models.TextField("Descripción", blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    token = models.CharField(max_length=64, unique=True, default=generate_presentation_token, editable=False)
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.MANUAL,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presentations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Presentación"
        verbose_name_plural = "Presentaciones"

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    def get_public_path(self):
        return reverse("public_player", kwargs={"token": self.token})

    def get_absolute_url(self):
        return reverse("presentations:editor", kwargs={"pk": self.pk})

    @property
    def is_powerpoint_import(self):
        return self.source_type == self.SourceType.POWERPOINT


class PowerPointImport(models.Model):
    """Registro de importación de archivos PowerPoint."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PROCESSING = "processing", "Procesando"
        COMPLETED = "completed", "Completada"
        FAILED = "failed", "Fallida"

    presentation = models.OneToOneField(
        Presentation,
        on_delete=models.CASCADE,
        related_name="powerpoint_import",
    )
    original_file = models.FileField(upload_to=powerpoint_original_path)
    original_filename = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    slide_count = models.PositiveIntegerField(default=0)
    processed_slide_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="powerpoint_imports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Importación PowerPoint"
        verbose_name_plural = "Importaciones PowerPoint"

    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()})"


class MediaAsset(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Imagen"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Documento"

    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name="media_assets",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to=media_upload_path)
    is_processed = models.BooleanField(
        default=False,
        help_text="True si el archivo fue generado por importación PowerPoint",
    )
    original_filename = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Archivo multimedia"
        verbose_name_plural = "Archivos multimedia"

    def __str__(self):
        return self.original_filename


class Slide(models.Model):
    class SlideType(models.TextChoices):
        TEXT = "text", "Texto"
        IMAGE = "image", "Imagen"
        VIDEO = "video", "Video"
        MIXED = "mixed", "Mixta"

    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name="slides",
    )
    order = models.PositiveIntegerField(default=0)
    slide_type = models.CharField(
        max_length=20,
        choices=SlideType.choices,
        default=SlideType.TEXT,
    )
    title = models.CharField("Título", max_length=200, blank=True)
    subtitle = models.CharField("Subtítulo", max_length=200, blank=True)
    content = models.TextField("Contenido", blank=True)
    duration = models.PositiveIntegerField("Duración (segundos)", default=10)
    background_color = models.CharField("Color de fondo", max_length=7, default="#1a1a2e")
    background_image = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="background_slides",
    )
    image = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="image_slides",
    )
    video = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_slides",
    )
    custom_content = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Diapositiva"
        verbose_name_plural = "Diapositivas"

    def __str__(self):
        return self.title or f"Diapositiva {self.order + 1}"

    def to_player_dict(self):
        """Serializa la diapositiva para el reproductor TV."""
        data = {
            "id": self.pk,
            "order": self.order,
            "type": self.slide_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "content": self.content,
            "duration": self.duration,
            "background_color": self.background_color,
            "custom_content": self.custom_content,
        }
        if self.background_image_id and self.background_image.file:
            data["background_image_url"] = self.background_image.file.url
        if self.image_id and self.image.file:
            data["image_url"] = self.image.file.url
        if self.video_id and self.video.file:
            data["video_url"] = self.video.file.url
        return data
