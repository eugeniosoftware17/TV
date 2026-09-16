from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from accounts.models import UserProfile

User = get_user_model()


class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.Role.choices,
        initial=UserProfile.Role.VIEWER,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rol",
    )

    class Meta:
        model = User
        fields = ["username", "email", "role"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.role = self.cleaned_data["role"]
            user.profile.save(update_fields=["role"])
        return user


class UserRoleForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.Role.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rol",
    )
    is_active = forms.BooleanField(required=False, label="Usuario activo")

    class Meta:
        model = User
        fields = ["is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["role"].initial = self.instance.profile.role

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.role = self.cleaned_data["role"]
            user.profile.save(update_fields=["role"])
        return user
