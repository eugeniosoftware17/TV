from django.urls import path

from presentations import public_views

urlpatterns = [
    path("<str:token>/", public_views.public_player, name="public_player"),
    path("<str:token>/data/", public_views.public_player_data, name="public_player_data"),
]
