from django.contrib import admin

from . import models


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'text', 'is_anonymous', 'created_at')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')


class PointAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'ip', 'count', 'created_at')


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'followee')


class MuteAdmin(admin.ModelAdmin):
    list_display = ('user', 'target')


admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.Point, PointAdmin)
admin.site.register(models.FriendShip, FriendshipAdmin)
admin.site.register(models.Mute, MuteAdmin)
