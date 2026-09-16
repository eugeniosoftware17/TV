from django.contrib import admin

from presentations.models import MediaAsset, PowerPointImport, Presentation, Slide


class SlideInline(admin.TabularInline):
    model = Slide
    extra = 0
    fields = ("order", "slide_type", "title", "duration")


@admin.register(PowerPointImport)
class PowerPointImportAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "presentation", "status", "slide_count", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "processed_at")


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "status", "token", "created_at", "updated_at")
    list_filter = ("status", "source_type")
    search_fields = ("name", "token")
    readonly_fields = ("token", "created_at", "updated_at")
    inlines = [SlideInline]


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("presentation", "order", "slide_type", "title", "duration")
    list_filter = ("slide_type",)
    search_fields = ("title", "presentation__name")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "media_type", "presentation", "file_size", "created_at")
    list_filter = ("media_type",)
