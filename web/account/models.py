from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils import timezone

import os
from uuid import uuid4
from core.utils import CustomModel
from .validators import UsernameValidator
from .ranking import Contribution

import twitter
from social_django.models import UserSocialAuth

ACCOUNT_CREATING_LIMIT_DAYS = 1
UPLOAD_LIMIT_MINUTES = 10


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

    followees = models.ManyToManyField('User', verbose_name='フォロー中のユーザー', through='ajax.FriendShip',
                                       related_name='followings+', through_fields=('user', 'followee'))
    followers = models.ManyToManyField('User', verbose_name='フォローされているユーザー', through='ajax.FriendShip',
                                       related_name='followers+', through_fields=('followee', 'user'))
    mutes = models.ManyToManyField('User', verbose_name='ミュート中のユーザー', through='ajax.Mute',
                                   related_name='+', through_fields=('user', 'target'))

    contribution_point = models.PositiveIntegerField('貢献ポイント', default=0, blank=True)
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
    def twitter_info(self):
        if self.has_twitter_auth:
            extra_data = self.social_auth.filter(provider='twitter').last().extra_data
            return extra_data['access_token']
        raise Exception('ツイッターの認証情報がありません')

    @property
    def api(self):
        social_auth_obj = UserSocialAuth.objects.filter(user=self).last()
        api = twitter.Api(consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                          consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                          access_token_key=social_auth_obj.extra_data['access_token']['oauth_token'],
                          access_token_secret=social_auth_obj.extra_data['access_token']['oauth_token_secret'],
                          tweet_mode='extended')
        return api

    @property
    def is_newcomer(self):
        return timezone.now() - self.date_joined < timezone.timedelta(days=1)

    @property
    def is_uploadable(self):
        latest_video = self.video_set.last()
        if not latest_video:
            return True
        elapsed_time = timezone.now() - latest_video.profile.created_at
        return not (self.is_newcomer and elapsed_time < timezone.timedelta(minutes=UPLOAD_LIMIT_MINUTES))

    @property
    def date_uploadable(self):
        latest_video = self.video_set.last()
        return latest_video.profile.created_at + timezone.timedelta(minutes=UPLOAD_LIMIT_MINUTES)

    @property
    def contribution(self):
        return Contribution(user=self)

    def calculate_contrib(self):
        self.contribution_point = self.contribution.point()
        self.save()

    def json(self):
        return {
            'username': self.username,
            'name': self.name,
            'is_staff': self.is_staff,
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


class AccessLog(CustomModel):
    user = models.OneToOneField(User, verbose_name='ユーザー', on_delete=models.CASCADE)
    # ip_joinedはIPモデル作成以降の参考記録
    # ipアドレスは取得に失敗する場合もあるのでフィールドはnull=True
    ip_joined = models.GenericIPAddressField('初回ログイン時のIP', null=True, blank=True)
    ip_latest = models.GenericIPAddressField('最終ログイン時のIP', null=True, blank=True)

    @property
    def allows_create_account(self):
        return timezone.now() - self.user.date_joined > timezone.timedelta(days=ACCOUNT_CREATING_LIMIT_DAYS)


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
