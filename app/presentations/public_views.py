from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from presentations.services import PresentationService
from screens.models import Screen


@never_cache
@require_GET
def public_player(request, token):
    presentation = PresentationService.get_by_token(token)
    if not presentation:
        return render(request, "presentations/public/not_found.html", status=404)
    if not presentation.is_active:
        return render(
            request,
            "presentations/public/inactive.html",
            {"presentation": presentation},
            status=403,
        )
    return render(
        request,
        "presentations/public/player.html",
        {
            "presentation": presentation,
            "data_url": f"/p/{token}/data/",
            "display_scale": presentation.display_scale,
            "display_scale_factor": presentation.display_scale / 100,
            "control_url": f"/p/{token}/control/",
        },
    )


@never_cache
@require_GET
def public_player_data(request, token):
    presentation = PresentationService.get_by_token(token)
    if not presentation:
        return JsonResponse({"error": "Presentación no encontrada"}, status=404)
    if not presentation.is_active:
        return JsonResponse({"error": "Presentación inactiva"}, status=403)

    data = PresentationService.get_player_data(presentation)
    return JsonResponse(data)


@never_cache
@require_GET
def public_player_control(request, token):
    presentation = PresentationService.get_by_token(token)
    if not presentation:
        return JsonResponse({"reload": False}, status=404)

    threshold = timezone.now() - timezone.timedelta(minutes=2)
    pending_screens = Screen.objects.filter(
        current_presentation=presentation,
        reload_requested=True,
    )

    reload_needed = pending_screens.filter(reload_requested_at__gte=threshold).exists()

    for screen in pending_screens:
        screen.reload_requested = False
        screen.save(update_fields=["reload_requested"])

    return JsonResponse({"reload": reload_needed})
