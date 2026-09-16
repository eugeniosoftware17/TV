from core.models import EventLog


class LoggingService:
    """Servicio centralizado para registrar eventos del sistema."""

    @staticmethod
    def log(event_type, message, *, user=None, presentation=None, screen=None, metadata=None):
        return EventLog.objects.create(
            event_type=event_type,
            message=message,
            user=user,
            presentation=presentation,
            screen=screen,
            metadata=metadata or {},
        )
