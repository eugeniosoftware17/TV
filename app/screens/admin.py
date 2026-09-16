from django.contrib import admin

from screens.models import Screen


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "location", "status", "last_seen", "current_presentation")
    list_filter = ("status",)
    search_fields = ("name", "identifier", "location")
    readonly_fields = ("identifier", "pairing_code", "session_id", "created_at", "updated_at")
