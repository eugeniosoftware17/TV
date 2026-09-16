from django import forms

from screens.models import Screen


class ScreenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ["name", "location", "current_presentation", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "TV-001"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Recepción"}),
            "current_presentation": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
