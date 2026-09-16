from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from screens.forms import ScreenForm
from screens.models import Screen
from screens.services import ScreenService


@login_required
def screen_list(request):
    screens = Screen.objects.select_related("current_presentation").all()
    return render(request, "screens/list.html", {"screens": screens})


@login_required
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


@login_required
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


@login_required
@require_POST
def screen_delete(request, pk):
    screen = get_object_or_404(Screen, pk=pk)
    ScreenService.delete(screen, user=request.user)
    messages.success(request, "Pantalla eliminada.")
    return redirect("screens:list")
