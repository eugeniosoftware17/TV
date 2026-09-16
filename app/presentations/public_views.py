from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from presentations.services import PresentationService


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
