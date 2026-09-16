from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import UserProfile
from accounts.permissions import role_required
from screens.forms import ScreenForm
from screens.models import Screen
from screens.services import ScreenService

ADMIN = UserProfile.Role.ADMIN


@role_required(ADMIN)
def screen_list(request):
    screens = Screen.objects.select_related("current_presentation").all()
    return render(request, "screens/list.html", {"screens": screens})


@role_required(ADMIN)
@require_http_methods(["GET", "POST"])
def screen_create(request):
    if request.method == "POST":
        form = ScreenForm(request.POST)
        if form.is_valid():
            ScreenService.create(
                name=form.cleaned_data["name"],
                location=form.cleaned_data["location"],
                current_presentation=form.cleaned_data["current_presentation"],
                user=request.user,
            )
            messages.success(request, "Pantalla registrada correctamente.")
            return redirect("screens:list")
    else:
        form = ScreenForm()
    return render(request, "screens/form.html", {"form": form, "title": "Registrar pantalla"})


@role_required(ADMIN)
@require_http_methods(["GET", "POST"])
def screen_edit(request, pk):
    screen = get_object_or_404(Screen, pk=pk)
    if request.method == "POST":
        form = ScreenForm(request.POST, instance=screen)
        if form.is_valid():
            ScreenService.update(
                screen,
                name=form.cleaned_data["name"],
                location=form.cleaned_data["location"],
                current_presentation=form.cleaned_data["current_presentation"],
                status=form.cleaned_data["status"],
                user=request.user,
            )
            messages.success(request, "Pantalla actualizada.")
            return redirect("screens:list")
    else:
        form = ScreenForm(instance=screen)
    return render(
        request,
        "screens/form.html",
        {"form": form, "screen": screen, "title": "Editar pantalla"},
    )


@role_required(ADMIN)
@require_POST
def screen_delete(request, pk):
    screen = get_object_or_404(Screen, pk=pk)
    ScreenService.delete(screen, user=request.user)
    messages.success(request, "Pantalla eliminada.")
    return redirect("screens:list")


@role_required(ADMIN)
@require_POST
def screen_reload(request, pk):
    screen = get_object_or_404(Screen, pk=pk)
    screen.reload_requested = True
    screen.reload_requested_at = timezone.now()
    screen.save(update_fields=["reload_requested", "reload_requested_at"])
    return JsonResponse({"success": True})
