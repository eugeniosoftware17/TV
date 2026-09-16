from django.contrib import admin

from core.models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "message", "user", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("message",)
    readonly_fields = ("created_at",)
