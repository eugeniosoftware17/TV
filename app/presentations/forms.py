from django import forms

from django.conf import settings

from presentations.models import Presentation, Slide
from presentations.validators import validate_media_file, validate_powerpoint_file


class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ["name", "description", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la presentación"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class SlideForm(forms.ModelForm):
    upload_image = forms.FileField(
        required=False,
        label="Subir imagen",
        validators=[validate_media_file],
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )
    upload_video = forms.FileField(
        required=False,
        label="Subir video",
        validators=[validate_media_file],
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "video/mp4,video/webm"}),
    )
    upload_background = forms.FileField(
        required=False,
        label="Subir fondo",
        validators=[validate_media_file],
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    class Meta:
        model = Slide
        fields = [
            "slide_type",
            "title",
            "subtitle",
            "content",
            "duration",
            "background_color",
        ]
        widgets = {
            "slide_type": forms.Select(attrs={"class": "form-select", "id": "id_slide_type"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 600}),
            "background_color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")
        if duration is not None and duration < 1:
            raise forms.ValidationError("La duración mínima es 1 segundo.")
        return duration


class PowerPointImportForm(forms.Form):
    name = forms.CharField(
        required=False,
        max_length=200,
        label="Nombre de la presentación",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Opcional — se usa el nombre del archivo",
        }),
    )
    file = forms.FileField(
        label="Archivo PowerPoint",
        validators=[validate_powerpoint_file],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": ".pptx,.ppt",
            "id": "id_powerpoint_file",
        }),
    )

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        validate_powerpoint_file(uploaded)
        return uploaded

    @staticmethod
    def max_size_mb():
        max_size = getattr(settings, "POWERPOINT_MAX_FILE_SIZE", 100 * 1024 * 1024)
        return max_size // (1024 * 1024)
