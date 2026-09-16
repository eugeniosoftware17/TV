from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.forms import UserCreateForm, UserRoleForm
from accounts.models import UserProfile
from accounts.permissions import role_required

User = get_user_model()


@role_required(UserProfile.Role.ADMIN)
def user_list(request):
    users = User.objects.select_related("profile").order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})


@role_required(UserProfile.Role.ADMIN)
@require_http_methods(["GET", "POST"])
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("accounts:user_list")
    else:
        form = UserCreateForm()
    return render(request, "accounts/user_form.html", {"form": form, "title": "Nuevo usuario"})


@role_required(UserProfile.Role.ADMIN)
@require_http_methods(["GET", "POST"])
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado.")
            return redirect("accounts:user_list")
    else:
        form = UserRoleForm(instance=user)
    return render(
        request,
        "accounts/user_form.html",
        {"form": form, "title": "Editar usuario", "edit_user": user},
    )
