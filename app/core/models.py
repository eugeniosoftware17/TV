from django.conf import settings
from django.db import models


class EventLog(models.Model):
    """Registro de eventos importantes del sistema."""

    class EventType(models.TextChoices):
        PRESENTATION_CREATED = "presentation_created", "Presentación creada"
        PRESENTATION_UPDATED = "presentation_updated", "Presentación modificada"
        PRESENTATION_DELETED = "presentation_deleted", "Presentación eliminada"
        PRESENTATION_DUPLICATED = "presentation_duplicated", "Presentación duplicada"
        PRESENTATION_TOGGLED = "presentation_toggled", "Estado de presentación cambiado"
        PRESENTATION_IMPORTED = "presentation_imported", "Presentación importada desde PowerPoint"
        PRESENTATION_IMPORT_FAILED = "presentation_import_failed", "Error al importar PowerPoint"
        SLIDE_CREATED = "slide_created", "Diapositiva creada"
        SLIDE_UPDATED = "slide_updated", "Diapositiva modificada"
        SLIDE_DELETED = "slide_deleted", "Diapositiva eliminada"
        SLIDE_REORDERED = "slide_reordered", "Diapositivas reordenadas"
        SCREEN_CONNECTED = "screen_connected", "Pantalla conectada"
        SCREEN_DISCONNECTED = "screen_disconnected", "Pantalla desconectada"
        SCREEN_PRESENTATION_CHANGED = "screen_presentation_changed", "Cambio de presentación en pantalla"

    event_type = models.CharField(max_length=50, choices=EventType.choices)
    message = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_logs",
    )
    presentation = models.ForeignKey(
        "presentations.Presentation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_logs",
    )
    screen = models.ForeignKey(
        "screens.Screen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_logs",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registro de evento"
        verbose_name_plural = "Registros de eventos"

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.created_at:%Y-%m-%d %H:%M}"
