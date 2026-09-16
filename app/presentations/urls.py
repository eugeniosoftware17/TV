from django.urls import path

from presentations import views

app_name = "presentations"

urlpatterns = [
    path("", views.presentation_list, name="list"),
    path("create/", views.presentation_create_choice, name="create"),
    path("create/manual/", views.presentation_create, name="create_manual"),
    path("import/", views.presentation_import_powerpoint, name="import_powerpoint"),
    path("import/<int:pk>/status/", views.presentation_import_status, name="import_status"),
    path("import/<int:pk>/status/api/", views.presentation_import_status_api, name="import_status_api"),
    path("<int:pk>/", views.presentation_detail, name="detail"),
    path("<int:pk>/edit/", views.presentation_edit, name="edit"),
    path("<int:pk>/editor/", views.presentation_editor, name="editor"),
    path("<int:pk>/delete/", views.presentation_delete, name="delete"),
    path("<int:pk>/duplicate/", views.presentation_duplicate, name="duplicate"),
    path("<int:pk>/toggle/", views.presentation_toggle, name="toggle"),
    path("<int:presentation_pk>/slides/create/", views.slide_create, name="slide_create"),
    path("<int:presentation_pk>/slides/reorder/", views.slide_reorder, name="slide_reorder"),
    path("<int:presentation_pk>/preview-data/", views.slide_preview_data, name="preview_data"),
    path("slides/<int:pk>/edit/", views.slide_edit, name="slide_edit"),
    path("slides/<int:pk>/delete/", views.slide_delete, name="slide_delete"),
    path("slides/<int:pk>/duplicate/", views.slide_duplicate, name="slide_duplicate"),
]
