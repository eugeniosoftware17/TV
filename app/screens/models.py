import secrets
import uuid

from django.db import models
from django.utils import timezone


def generate_screen_identifier():
    return f"TV-{secrets.token_hex(3).upper()}"


def generate_pairing_code():
    return secrets.token_hex(4).upper()


class Screen(models.Model):
    """
    Representa un televisor registrado en el sistema.
    Preparado para vinculación individual en Fase 2.
    """

    class Status(models.TextChoices):
        CONNECTED = "connected", "Conectada"
        DISCONNECTED = "disconnected", "Desconectada"
        PENDING = "pending", "Pendiente de vinculación"

    name = models.CharField("Nombre", max_length=100)
    location = models.CharField("Ubicación", max_length=200, blank=True)
    identifier = models.CharField(
        max_length=32,
        unique=True,
        default=generate_screen_identifier,
        editable=False,
    )
    pairing_code = models.CharField(
        max_length=16,
        default=generate_pairing_code,
        blank=True,
        help_text="Código para vincular la pantalla (Fase 2)",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    last_seen = models.DateTimeField(null=True, blank=True)
    current_presentation = models.ForeignKey(
        "presentations.Presentation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="screens",
    )
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Pantalla"
        verbose_name_plural = "Pantallas"

    def __str__(self):
        return self.name

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        threshold = timezone.now() - timezone.timedelta(seconds=60)
        return self.last_seen >= threshold or self.status == self.Status.CONNECTED

    def mark_connected(self, presentation=None):
        self.status = self.Status.CONNECTED
        self.last_seen = timezone.now()
        if presentation:
            self.current_presentation = presentation
        self.save(update_fields=["status", "last_seen", "current_presentation", "updated_at"])

    def mark_disconnected(self):
        self.status = self.Status.DISCONNECTED
        self.save(update_fields=["status", "updated_at"])
