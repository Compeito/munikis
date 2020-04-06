from django.contrib import admin

from browse.models import VideoProfileLabelRelation
from . import models


class ReadOnlyMixin:
    def has_change_permission(self, request, obj=None):
        return False


class VideoAdmin(admin.ModelAdmin):
    class VideoProfileInline(admin.StackedInline):
        model = models.VideoProfile

    class VideoDataInline(ReadOnlyMixin, admin.StackedInline):
        model = models.VideoData

    list_display = (
        'id', 'user', 'slug',
        'is_pickup', 'is_ban', 'published_at',
        'views_count', 'type', 'source_url'
    )
    list_filter = ('is_pickup', 'type')
    inlines = (VideoProfileInline, VideoDataInline)


class UploadedPureVideo(admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'updated_at',
        'video', 'file', 'is_encoding',
        'is_failed',
    )


class VideoProfileAdmin(admin.ModelAdmin):
    class LabelInline(admin.TabularInline):
        model = VideoProfileLabelRelation

    list_display = (
        'id', 'created_at', 'updated_at',
        'release_type', 'video', 'title',
        'file', 'ordered_fps', 'is_loop',
        'allows_anonymous_comment', 'labels_str'
    )
    search_fields = ('title',)
    list_filter = ('labels',)
    inlines = (LabelInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('video').prefetch_related('labels')


class VideoDataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'video', 'thumbnail',
        'gif', 'file', 'fps',
        'duration'
    )


admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.UploadedPureVideo, UploadedPureVideo)
admin.site.register(models.VideoProfile, VideoProfileAdmin)
admin.site.register(models.VideoData, VideoDataAdmin)
