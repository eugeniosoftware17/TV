from django.urls import path, register_converter

from presentations import public_views


class PresentationTokenConverter:
    """Código numérico de 3 dígitos con ceros a la izquierda (001-999)."""

    regex = "[0-9]{3}"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(PresentationTokenConverter, "pres_token")

urlpatterns = [
    path("<pres_token:token>/", public_views.public_player, name="public_player"),
    path("<pres_token:token>/data/", public_views.public_player_data, name="public_player_data"),
    path("<pres_token:token>/control/", public_views.public_player_control, name="public_player_control"),
]
