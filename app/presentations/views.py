import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import UserProfile
from accounts.permissions import role_required
from presentations.forms import PowerPointImportForm, PresentationForm, SlideForm
from presentations.models import PowerPointImport, Presentation, Slide
from presentations.services import MediaService, PowerPointImportService, PresentationService, SlideService

ADMIN = UserProfile.Role.ADMIN
EDITOR = UserProfile.Role.EDITOR
VIEWER = UserProfile.Role.VIEWER


@role_required(ADMIN, EDITOR, VIEWER)
def presentation_list(request):
    presentations = Presentation.objects.all()
    return render(request, "presentations/list.html", {"presentations": presentations})


@role_required(ADMIN, EDITOR)
def presentation_create_choice(request):
    return render(request, "presentations/create_choice.html")


@role_required(ADMIN, EDITOR)
@require_http_methods(["GET", "POST"])
def presentation_create(request):
    if request.method == "POST":
        form = PresentationForm(request.POST)
        if form.is_valid():
            presentation = PresentationService.create(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                status=form.cleaned_data["status"],
                display_scale=form.cleaned_data["display_scale"],
                user=request.user,
            )
            messages.success(request, "Presentación creada correctamente.")
            return redirect("presentations:editor", pk=presentation.pk)
    else:
        form = PresentationForm(initial={"status": Presentation.Status.ACTIVE})
    return render(request, "presentations/form.html", {"form": form, "title": "Nueva presentación"})


@role_required(ADMIN, EDITOR)
@require_http_methods(["GET", "POST"])
def presentation_import_powerpoint(request):
    if request.method == "POST":
        form = PowerPointImportForm(request.POST, request.FILES)
        if form.is_valid():
            ppt_import = PowerPointImportService.start_import(
                uploaded_file=form.cleaned_data["file"],
                name=form.cleaned_data.get("name") or None,
                user=request.user,
            )
            return redirect("presentations:import_status", pk=ppt_import.pk)
    else:
        form = PowerPointImportForm()
    return render(
        request,
        "presentations/import_powerpoint.html",
        {"form": form, "max_size_mb": PowerPointImportForm.max_size_mb()},
    )


@role_required(ADMIN, EDITOR)
def presentation_import_status(request, pk):
    ppt_import = get_object_or_404(PowerPointImport, pk=pk)
    return render(
        request,
        "presentations/import_status.html",
        {"ppt_import": ppt_import},
    )


@role_required(ADMIN, EDITOR)
def presentation_import_status_api(request, pk):
    ppt_import = get_object_or_404(PowerPointImport, pk=pk)
    return JsonResponse(PowerPointImportService.get_status_payload(ppt_import))


@role_required(ADMIN, EDITOR)
@require_http_methods(["GET", "POST"])
def presentation_edit(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    if request.method == "POST":
        form = PresentationForm(request.POST, instance=presentation)
        if form.is_valid():
            PresentationService.update(
                presentation,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                status=form.cleaned_data["status"],
                display_scale=form.cleaned_data["display_scale"],
                user=request.user,
            )
            messages.success(request, "Presentación actualizada.")
            return redirect("presentations:detail", pk=presentation.pk)
    else:
        form = PresentationForm(instance=presentation)
    return render(
        request,
        "presentations/form.html",
        {"form": form, "presentation": presentation, "title": "Editar presentación"},
    )


@role_required(ADMIN, EDITOR, VIEWER)
def presentation_detail(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    public_url = request.build_absolute_uri(presentation.get_public_path())
    return render(
        request,
        "presentations/detail.html",
        {"presentation": presentation, "public_url": public_url},
    )


@role_required(ADMIN, EDITOR)
def presentation_editor(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    slides = presentation.slides.all()
    public_url = request.build_absolute_uri(presentation.get_public_path())
    return render(
        request,
        "presentations/editor.html",
        {"presentation": presentation, "slides": slides, "public_url": public_url},
    )


@role_required(ADMIN)
@require_POST
def presentation_delete(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    PresentationService.delete(presentation, user=request.user)
    messages.success(request, "Presentación eliminada.")
    return redirect("presentations:list")


@role_required(ADMIN, EDITOR)
@require_POST
def presentation_duplicate(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    new_presentation = PresentationService.duplicate(presentation, user=request.user)
    messages.success(request, "Presentación duplicada.")
    return redirect("presentations:editor", pk=new_presentation.pk)


@role_required(ADMIN, EDITOR)
@require_POST
def presentation_toggle(request, pk):
    presentation = get_object_or_404(Presentation, pk=pk)
    PresentationService.toggle_status(presentation, user=request.user)
    status_label = presentation.get_status_display()
    messages.success(request, f"Estado cambiado a: {status_label}")
    return redirect(request.META.get("HTTP_REFERER", "presentations:list"))


@role_required(ADMIN, EDITOR)
@require_http_methods(["GET", "POST"])
def slide_create(request, presentation_pk):
    presentation = get_object_or_404(Presentation, pk=presentation_pk)
    if request.method == "POST":
        form = SlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = SlideService.create(
                presentation,
                slide_type=form.cleaned_data["slide_type"],
                title=form.cleaned_data["title"],
                subtitle=form.cleaned_data["subtitle"],
                content=form.cleaned_data["content"],
                duration=form.cleaned_data["duration"],
                background_color=form.cleaned_data["background_color"],
                user=request.user,
            )
            if form.cleaned_data.get("upload_image"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_image"], user=request.user)
                slide.image = media
                slide.save()
            if form.cleaned_data.get("upload_video"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_video"], user=request.user)
                slide.video = media
                slide.save()
            if form.cleaned_data.get("upload_background"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_background"], user=request.user)
                slide.background_image = media
                slide.save()
            messages.success(request, "Diapositiva creada.")
            return redirect("presentations:editor", pk=presentation.pk)
    else:
        slide_type = request.GET.get("type", Slide.SlideType.TEXT)
        form = SlideForm(initial={"slide_type": slide_type, "duration": 10})
    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation": presentation, "title": "Nueva diapositiva"},
    )


@role_required(ADMIN, EDITOR)
@require_http_methods(["GET", "POST"])
def slide_edit(request, pk):
    slide = get_object_or_404(Slide, pk=pk)
    presentation = slide.presentation
    if request.method == "POST":
        form = SlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            SlideService.update(
                slide,
                slide_type=form.cleaned_data["slide_type"],
                title=form.cleaned_data["title"],
                subtitle=form.cleaned_data["subtitle"],
                content=form.cleaned_data["content"],
                duration=form.cleaned_data["duration"],
                background_color=form.cleaned_data["background_color"],
                user=request.user,
            )
            if form.cleaned_data.get("upload_image"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_image"], user=request.user)
                slide.image = media
                slide.save()
            if form.cleaned_data.get("upload_video"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_video"], user=request.user)
                slide.video = media
                slide.save()
            if form.cleaned_data.get("upload_background"):
                media = MediaService.upload(presentation, form.cleaned_data["upload_background"], user=request.user)
                slide.background_image = media
                slide.save()
            messages.success(request, "Diapositiva actualizada.")
            return redirect("presentations:editor", pk=presentation.pk)
    else:
        form = SlideForm(instance=slide)
    return render(
        request,
        "presentations/slide_form.html",
        {"form": form, "presentation": presentation, "slide": slide, "title": "Editar diapositiva"},
    )


@role_required(ADMIN)
@require_POST
def slide_delete(request, pk):
    slide = get_object_or_404(Slide, pk=pk)
    presentation_pk = slide.presentation_id
    SlideService.delete(slide, user=request.user)
    messages.success(request, "Diapositiva eliminada.")
    return redirect("presentations:editor", pk=presentation_pk)


@role_required(ADMIN, EDITOR)
@require_POST
def slide_duplicate(request, pk):
    slide = get_object_or_404(Slide, pk=pk)
    SlideService.duplicate(slide, user=request.user)
    messages.success(request, "Diapositiva duplicada.")
    return redirect("presentations:editor", pk=slide.presentation_id)


@role_required(ADMIN, EDITOR)
@require_POST
def slide_reorder(request, presentation_pk):
    presentation = get_object_or_404(Presentation, pk=presentation_pk)
    try:
        payload = json.loads(request.body)
        slide_ids = payload.get("order", [])
        if not isinstance(slide_ids, list):
            return JsonResponse({"error": "Formato inválido"}, status=400)
        slide_ids = [int(sid) for sid in slide_ids]
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "JSON inválido"}, status=400)

    valid_ids = set(presentation.slides.filter(pk__in=slide_ids).values_list("pk", flat=True))
    if len(valid_ids) != len(slide_ids):
        return JsonResponse({"error": "IDs de diapositiva inválidos"}, status=400)

    SlideService.reorder(presentation, slide_ids, user=request.user)
    return JsonResponse({"success": True})


@role_required(ADMIN, EDITOR, VIEWER)
def slide_preview_data(request, presentation_pk):
    presentation = get_object_or_404(Presentation, pk=presentation_pk)
    data = PresentationService.get_player_data(presentation)
    if data is None:
        data = {
            "name": presentation.name,
            "slides": [s.to_player_dict() for s in presentation.slides.all()],
            "version": int(presentation.updated_at.timestamp()),
        }
    return JsonResponse(data)
