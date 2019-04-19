from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

import os
from uuid import uuid4
from core.utils import CustomModel, created_at2str, anonymous_names
from notify.models import Notification
from .validators import UsernameValidator

import twitter
from social_django.models import UserSocialAuth


def profile_image_upload_to(instance, filename):
    return os.path.join('u', instance.username, 'profile', f'{uuid4().hex}.jpg')


class User(AbstractUser):
    username_validator = UsernameValidator()
    username = models.CharField('ユーザー名', max_length=20, unique=True, validators=[username_validator])

    # createsuperuserなどのためにnull許容
    name = models.CharField('表示名', max_length=50, null=True)
    description = models.TextField('プロフィール文', default='', max_length=500, null=True, blank=True)

    profile_icon = models.ImageField('プロフィール画像', upload_to=profile_image_upload_to, null=True, blank=True)
    profile_banner = models.ImageField('プロフィール背景画像', upload_to=profile_image_upload_to, null=True, blank=True)

    is_accept_mail = models.BooleanField('メール配信の許可', default=True)
    objects = UserManager()

    @property
    def profile_icon_url(self):
        if self.profile_icon:
            return self.profile_icon.url
        return '/assets/images/default-icon.png'

    @property
    def profile_banner_url(self):
        if self.profile_banner:
            return self.profile_banner.url
        return '/assets/images/default-banner.png'

    @property
    def has_twitter_auth(self):
        return self.social_auth.filter(provider='twitter').exists()

    @property
    def has_altwug_auth(self):
        return hasattr(self, 'altwugauth')

    @property
    def extra_data(self):
        if self.has_twitter_auth:
            return self.social_auth.get(provider='twitter').extra_data

    @property
    def api(self):
        social_auth_obj = UserSocialAuth.objects.get(user=self)
        api = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                          consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                          access_token_key=social_auth_obj.extra_data['access_token']['oauth_token'],
                          access_token_secret=social_auth_obj.extra_data['access_token']['oauth_token_secret'],
                          tweet_mode='extended')
        return api

    def json(self):
        return {
            'username': self.username,
            'name': self.name,
            'profile_icon_url': self.profile_icon_url,
            'profile_banner_url': self.profile_banner_url,
        }

    def __str__(self):
        return f'{self.name}(@{self.username})'

    def delete(self, **kwargs):
        self.profile_icon.delete(False)
        self.profile_banner.delete(False)
        return super().delete(**kwargs)

    class Meta(object):
        app_label = 'account'


class AltwugAuth(CustomModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_id = models.IntegerField()


def trophy_upload_to(self, filename):
    extension = os.path.splitext(filename)[1]
    return os.path.join('trophy', f'{uuid4().hex}{extension}')


class Trophy(CustomModel):
    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    file = models.FileField(upload_to=trophy_upload_to)

    def __str__(self):
        return self.title


class TrophyUserRelation(CustomModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trophy = models.ForeignKey(Trophy, on_delete=models.CASCADE)


class DirectMessage(CustomModel):
    sender = models.ForeignKey(User, verbose_name='送り主', on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, verbose_name='受取先', on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField('DM本文', default='', max_length=300)
    is_anonymous = models.BooleanField('DMを匿名にする', default=False)

    def json(self):
        return {
            'sender_name': self.sender_name(),
            'sender_username': self.sender_username(),
            'sender_profile_icon': self.sender_profile_icon_url(),
            'recipient': self.recipient.json(),
            'text': self.text,
            'created_at': created_at2str(self.created_at),
            'is_anonymous': self.is_anonymous
        }

    @property
    def sender_name(self):
        if self.is_anonymous:
            index = int(self.sender.username.encode()[-1]) % len(anonymous_names)
            return anonymous_names[index]
        return self.sender.name

    @property
    def sender_username(self):
        if self.is_anonymous:
            return ""
        return self.sender.username

    @property
    def sender_profile_icon_url(self):
        if self.is_anonymous:
            return '/assets/images/default-icon.png'
        return self.sender.profile_icon_url

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.recipient == self.sender:
            Notification.objects.create(recipient=self.recipient, sender=self.sender, target=self)
