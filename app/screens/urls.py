from django.urls import path

from screens import views

app_name = "screens"

urlpatterns = [
    path("", views.screen_list, name="list"),
    path("create/", views.screen_create, name="create"),
    path("<int:pk>/edit/", views.screen_edit, name="edit"),
    path("<int:pk>/delete/", views.screen_delete, name="delete"),
    path("<int:pk>/reload/", views.screen_reload, name="reload"),
]
