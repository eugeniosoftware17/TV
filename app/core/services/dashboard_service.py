from django.db.models import Count, Q
from django.utils import timezone

from core.models import EventLog
from presentations.models import Presentation
from screens.models import Screen


class DashboardService:
    """Agrega estadísticas para el dashboard administrativo."""

    @staticmethod
    def get_stats():
        now = timezone.now()
        offline_threshold = now - timezone.timedelta(seconds=60)

        presentations = Presentation.objects.all()
        screens = Screen.objects.all()

        connected_screens = screens.filter(
            Q(status=Screen.Status.CONNECTED)
            | Q(last_seen__gte=offline_threshold)
        ).distinct()

        return {
            "total_presentations": presentations.count(),
            "active_presentations": presentations.filter(status=Presentation.Status.ACTIVE).count(),
            "connected_screens": connected_screens.count(),
            "offline_screens": screens.count() - connected_screens.count(),
            "recent_presentations": presentations.order_by("-updated_at")[:5],
            "recent_events": EventLog.objects.select_related("user", "presentation", "screen")[:10],
        }
