from django.db import models
from django.utils import timezone

from notify.models import Notification
from core.utils import created_at2str, CustomModel, activate_url_from
from .utils import get_anonymous_name


class Comment(models.Model):
    user = models.ForeignKey('account.User', verbose_name='ユーザー', on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)
    video = models.ForeignKey('upload.Video', verbose_name='動画', on_delete=models.CASCADE)
    text = models.TextField('本文', max_length=200)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    @property
    def user_name(self):
        if self.is_anonymous:
            return get_anonymous_name(self.user.username)
        return self.user.name

    @property
    def user_username(self):
        if self.is_anonymous:
            return ""
        return self.user.username

    @property
    def user_profile_icon_url(self):
        if self.is_anonymous:
            return '/assets/images/default-icon.png'
        return self.user.profile_icon_url

    def json(self, user):
        is_mine = False
        if user and user.is_authenticated:
            is_mine = user.username == self.user.username
        return {
            'id': self.id,
            'name': self.user_name,
            'username': self.user_username,
            'is_staff': self.user.is_staff,
            'profile_icon_url': self.user_profile_icon_url,
            'is_anonymous': self.is_anonymous,
            'is_mine': is_mine,
            'text': self.text,
            'html': activate_url_from(self.text),
            'createdAt': created_at2str(self.created_at)
        }

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.user == self.video.user:
            Notification.objects.create(recipient=self.video.user, sender=self.user, target=self)


class Point(CustomModel):
    user = models.ForeignKey('account.User', verbose_name='ユーザー', blank=True, null=True, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField('IPアドレス', blank=True, null=True)
    video = models.ForeignKey('upload.Video', verbose_name='動画', on_delete=models.CASCADE)
    count = models.PositiveIntegerField('ポイント')

    def json(self):
        return {
            'id': self.id,
            'user': self.user.json() if self.user else None,
            'username': self.user_name,
            'count': self.count,
            'createdAt': created_at2str(self.created_at)
        }

    @property
    def user_name(self):
        if self.user:
            return self.user.name
        return get_anonymous_name(self.ip)


class Favorite(CustomModel):
    user = models.ForeignKey('account.User', verbose_name='ユーザー', on_delete=models.CASCADE)
    video = models.ForeignKey('upload.Video', verbose_name='動画', on_delete=models.CASCADE)

    def json(self):
        return {
            'id': self.id,
            'user': self.user.json(),
            'createdAt': created_at2str(self.created_at)
        }

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.user == self.video.user:
            Notification.objects.create(recipient=self.video.user, sender=self.user, target=self)


class FriendShip(CustomModel):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='followee_friendships')
    followee = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='follower_friendships')

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.user == self.followee:
            Notification.objects.create(recipient=self.followee, sender=self.user, target=self)

    class Meta:
        unique_together = ('user', 'followee')
