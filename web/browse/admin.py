from django.contrib import admin
from . import models


class RankingAdmin(admin.ModelAdmin):
    list_display = ('point', 'video', 'day', 'type')


class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'icon', 'color', 'description')


class VideoProfileLabelRelationAdmin(admin.ModelAdmin):
    list_display = ('label', 'profile')


admin.site.register(models.Ranking, RankingAdmin)
admin.site.register(models.Label, LabelAdmin)
admin.site.register(models.VideoProfileLabelRelation, VideoProfileLabelRelationAdmin)
