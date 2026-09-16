from core.models import EventLog
from core.services import LoggingService
from screens.models import Screen


class ScreenService:
    @staticmethod
    def create(*, name, location="", current_presentation=None, user=None):
        screen = Screen.objects.create(
            name=name,
            location=location,
            current_presentation=current_presentation,
            status=Screen.Status.DISCONNECTED,
        )
        LoggingService.log(
            EventLog.EventType.SCREEN_CONNECTED,
            f"Pantalla registrada: {screen.name}",
            user=user,
            screen=screen,
        )
        return screen

    @staticmethod
    def update(screen, *, name, location, current_presentation, status, user=None):
        old_presentation_id = screen.current_presentation_id
        screen.name = name
        screen.location = location
        screen.current_presentation = current_presentation
        screen.status = status
        screen.save()

        if old_presentation_id != (current_presentation.pk if current_presentation else None):
            LoggingService.log(
                EventLog.EventType.SCREEN_PRESENTATION_CHANGED,
                f"Presentación cambiada en {screen.name}",
                user=user,
                screen=screen,
                presentation=current_presentation,
            )
        return screen

    @staticmethod
    def delete(screen, *, user=None):
        name = screen.name
        screen.delete()
        LoggingService.log(
            EventLog.EventType.SCREEN_DISCONNECTED,
            f"Pantalla eliminada: {name}",
            user=user,
        )

    @staticmethod
    def heartbeat(screen, *, presentation=None):
        screen.mark_connected(presentation=presentation)
        LoggingService.log(
            EventLog.EventType.SCREEN_CONNECTED,
            f"Pantalla conectada: {screen.name}",
            screen=screen,
            presentation=presentation,
        )
