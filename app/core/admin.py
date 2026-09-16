from django.contrib import admin

from core.models import EventLog, SiteSettings


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "message", "user", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("message",)
    readonly_fields = ("created_at",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "browser_title")
    fieldsets = (
        ("General", {"fields": ("site_name", "browser_title", "favicon")}),
        ("Logo del sidebar", {"fields": ("site_logo", "sidebar_logo_width")}),
        ("Logo de login", {"fields": ("login_logo", "login_logo_width")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SiteSettings.get_solo()
        return self.change_view(request, str(settings_obj.pk), extra_context=extra_context)
