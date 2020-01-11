from django.contrib import admin

from browse.models import VideoProfileLabelRelation
from . import models


class ReadOnlyMixin:
    def has_change_permission(self, request, obj=None):
        return False


class LabelInline(admin.TabularInline):
    model = VideoProfileLabelRelation


class VideoProfileInline(admin.StackedInline):
    model = models.VideoProfile


class VideoDataInline(ReadOnlyMixin, admin.StackedInline):
    model = models.VideoData


class VideoAdmin(admin.ModelAdmin):
    list_display_custom = [
        ('動画ID', 'slug', str),
        ('タイトル', 'profile__title', str),
        ('再生回数', 'views_count', int),
        ('公開状態', 'profile__get_release_type_display', str),
        ('BAN', 'is_ban', bool),
        ('作成日', 'profile__created_at', None)
    ]
    inlines = (VideoProfileInline, VideoDataInline)

    def get_list_display(self, request):

        def get_field_and_function(attr_path):
            attrs = attr_path.split('__')

            def field_func(instance):
                r = instance
                for attr in attrs:
                    if hasattr(r, attr):
                        r = getattr(r, attr)
                    else:
                        r = None
                        break
                return r if not callable(r) else r()

            return attrs[-1], field_func

        list_display = []
        for field_title, field_attr, field_type in self.list_display_custom:
            field, field_function = get_field_and_function(field_attr)

            field_function.short_description = field_title
            if field_type == bool:
                field_function.boolean = True
            setattr(self, field, field_function)

            list_display.append(field)

        return list_display


class VideoProfileAdmin(admin.ModelAdmin):
    inlines = (LabelInline,)


admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.UploadedPureVideo)
admin.site.register(models.VideoProfile, VideoProfileAdmin)
admin.site.register(models.VideoData)
