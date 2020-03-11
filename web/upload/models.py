import os
import random
import mimetypes
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property
from django.utils import timezone
from moviepy.editor import VideoFileClip

from .validators import FileValidator, video_file_validator, zip_validator
from .utils import get_tempfile
from browse.models import Ranking, Label, VideoProfileLabelRelation
from core.utils import CustomModel, gen_unique_slug


def default_video_slug():
    return gen_unique_slug(5, Video)


def video_upload_to(instance: 'VideoData', filename):
    return os.path.join('u', instance.video.user.username, 'videos', instance.video.slug, f'{uuid4().hex}.mp4')


def temp_upload_to(instance: 'UploadedPureVideo', filename):
    file_extension = filename.split('.')[-1]
    return os.path.join('temp', f'{instance.video.slug}-{timezone.now().strftime("%Y%m%d%H%M%S")}.{file_extension}')


def profile_upload_to(instance: 'VideoProfile', filename):
    return os.path.join('u', instance.video.user.username, 'videos', instance.video.slug, filename)


def thumbnail_upload_to(instance: 'VideoData', filename):
    return os.path.join('u', instance.video.user.username, 'videos', instance.video.slug, f'{uuid4().hex}.jpg')


def gif_upload_to(instance: 'VideoData', filename):
    return os.path.join('u', instance.video.user.username, 'videos', instance.video.slug, f'{uuid4().hex}.gif')


class Video(models.Model):
    """
    関連モデルを統括する基礎モデル
    """
    VIDEO_TYPES = (
        ('normal', '通常投稿'),
        ('updated', '通常投稿(再投稿済み)'),
        ('twitter', 'ツイッターからインポート'),
        ('altwug', 'Altwugからインポート'),
    )
    user = models.ForeignKey('account.User', verbose_name='投稿者', on_delete=models.CASCADE)
    slug = models.CharField('動画ID', max_length=5, default=default_video_slug, editable=False)

    is_pickup = models.BooleanField('ピックアップ', default=False)
    is_ban = models.BooleanField('運営による非公開', default=False)
    published_at = models.DateTimeField('公開時間', blank=True, null=True)

    views_count = models.PositiveIntegerField('再生回数', default=0)
    type = models.CharField('動画タイプ', max_length=20, choices=VIDEO_TYPES, default=VIDEO_TYPES[0][0])
    source_url = models.URLField('インポート元URL', null=True, blank=True)

    @property
    def type_icon(self):
        icons = {
            'twitter': 'fab fa-twitter',
            'altwug': 'fas fa-frog',
        }
        return icons[self.type]

    @property
    def is_encoded(self):
        return hasattr(self, 'data')

    @property
    def is_encoding(self):
        return hasattr(self, 'pure') and self.pure.is_encoding and not self.pure.is_failed

    @property
    def is_failed(self):
        return hasattr(self, 'pure') and self.pure.is_encoding and self.pure.is_failed

    @property
    def image_urls(self):
        thumbnail = 'https://tsukuriga.net/assets/images/ogp.png'
        gif = ''
        if hasattr(self, 'data') and not self.is_ban:
            if self.data.thumbnail:
                thumbnail = self.data.thumbnail.url
            if self.data.gif:
                gif = self.data.gif.url
        return {'thumbnail': thumbnail, 'gif': gif}

    @property
    def encode_state_display(self):
        if self.is_encoded:
            return 'エンコード完了'
        elif self.is_encoding:
            return 'エンコード中'
        elif self.is_failed:
            return 'エンコード失敗'
        return '未エンコード'

    @property
    def points_count(self):
        points = self.point_set.all()
        return sum([point.count for point in points])

    @property
    def point_users_count(self):
        users_count = self.point_set.filter(user__isnull=False).values('user').distinct().count()
        anonymous_count = self.point_set.filter(user__isnull=True).values('ip').distinct().count()
        return users_count + anonymous_count

    @property
    def favorites_count(self):
        return len(self.favorite_set.all())

    @property
    def commentators_count(self):
        return self.comment_set.exclude(user=self.user).values('user').distinct().count()

    def calculate_rankings(self):
        for ranking_day, i in Ranking.DAYS:
            for ranking_type, j in Ranking.TYPES:
                ranking = self.ranking_set.create(day=ranking_day, type=ranking_type)
                ranking.calculate()
                ranking.save()

    @property
    def published_at_str(self):
        return self.published_at.strftime('%Y-%m-%d_%H:%M:%S')

    def __str__(self):
        return self.profile.title + f'(id:{self.slug})'

    def delete(self, **kwargs):
        if hasattr(self, 'profile'):
            self.profile.delete()
        if hasattr(self, 'data'):
            self.data.delete()
        return super().delete(**kwargs)


class UploadedPureVideo(CustomModel):
    """
    エンコード前の未処理ファイルが保持されるモデル
    """
    video = models.OneToOneField(Video, verbose_name='動画', on_delete=models.CASCADE, related_name='pure')

    file_validator = FileValidator(allowed_extensions=['mp4', 'avi', 'gif', 'mov'], max_size=100 * 1024 * 1024)
    file = models.FileField('動画ファイル', upload_to=temp_upload_to, storage=FileSystemStorage(),
                            validators=[file_validator, video_file_validator])

    is_encoding = models.BooleanField('エンコード開始済み', default=False)
    is_failed = models.BooleanField('エンコード失敗', default=False)
    traceback = models.TextField('トレースバック', blank=True, null=True)

    @cached_property
    def clip(self):
        return VideoFileClip(self.file.path)

    def is_mp4(self):
        return mimetypes.guess_type(self.file.path)[0] == 'video/mp4'

    def create_thumbnail(self):
        filepath = get_tempfile('.jpg')
        t = random.randint(0, int(self.clip.duration))
        self.clip.save_frame(filepath, t=t)
        return filepath

    def encode_file(self):
        encoded_path = get_tempfile('.mp4')
        self.clip.write_videofile(encoded_path, **settings.ENCODE_OPTIONS)
        return encoded_path

    def make(self):
        self.is_encoding = True
        self.save()

        thumbnail_filepath = self.create_thumbnail()
        encoded_filepath = self.encode_file()

        with open(encoded_filepath, 'rb') as file, open(thumbnail_filepath, 'rb') as thumbnail:
            VideoData.objects.create(
                video=self.video,
                thumbnail=File(thumbnail),
                file=File(file),
                fps=self.clip.fps,
                duration=self.clip.duration
            )

        self.clip.close()

    def delete(self, **kwargs):
        if os.path.exists(self.file.path):
            os.remove(self.file.path)
        return super().delete(**kwargs)


class VideoProfile(CustomModel):
    """
    アップロード直後に情報が保持されるモデル
    基本的にユーザーが編集可
    """
    RELEASE_TYPES = (
        ('published', '公開'),
        ('limited', '限定公開'),
        ('unpublished', '未公開'),
    )
    release_type = models.CharField('公開状態', max_length=20, choices=RELEASE_TYPES, default=RELEASE_TYPES[-1][0])

    video = models.OneToOneField(Video, verbose_name='動画', on_delete=models.CASCADE, related_name='profile')
    labels = models.ManyToManyField(Label, verbose_name='ラベル', blank=True, through=VideoProfileLabelRelation)
    title = models.CharField('タイトル', max_length=50)
    description = models.TextField('動画説明', default='', max_length=200, null=True, blank=True)

    file_validator = FileValidator(allowed_extensions=['zip'], max_size=100 * 1024 * 1024)
    file = models.FileField(
        '添付ファイル', upload_to=profile_upload_to, validators=[file_validator, zip_validator], null=True, blank=True,
        help_text='動画出力前のデータ(pclx, kwzなど)を配布したい方向け。zip形式のみ対応で100MBまで',
    )

    ordered_fps = models.PositiveSmallIntegerField('fps', null=True, blank=True)
    is_loop = models.BooleanField('ループさせる', default=False, blank=True)
    allows_anonymous_comment = models.BooleanField('匿名コメントを許可', default=True, blank=True)

    @property
    def fps(self):
        if self.ordered_fps:
            return self.ordered_fps
        return self.video.data.fps

    @property
    def release_type_display(self):
        if self.video.is_ban:
            return '運営による非公開'
        return self.get_release_type_display()

    @cached_property
    def meta_title(self):
        return f'{self.title} | ' + (f'[{self.labels.first().title}]のアニメーション' if self.labels.exists() else 'アニメーション')

    @cached_property
    def meta_description(self):
        labels_str = ",".join([l.title for l in self.labels.all()])
        suffix = f'[{labels_str}]の自主制作アニメ、パラパラ漫画' if labels_str else '自主制作アニメ、パラパラ漫画'

        if len(self.description) > 60:
            return self.description[:60] + ' ... ' + suffix

        if not self.description:
            return suffix

        return self.description + ' ' + suffix

    def __str__(self):
        return self.video.__str__() + 'のプロフィール'


class VideoData(models.Model):
    """
    エンコード後に作成され、情報が保持されるモデル
    基本的にユーザーが編集不可
    """
    video = models.OneToOneField(Video, verbose_name='動画', on_delete=models.CASCADE, related_name='data')
    thumbnail = models.ImageField('サムネイル', upload_to=thumbnail_upload_to)
    gif = models.FileField('gifサムネイル', upload_to=gif_upload_to, blank=True, null=True)
    file = models.FileField('動画ファイル', upload_to=video_upload_to)
    fps = models.PositiveIntegerField('FPS')
    duration = models.FloatField('動画時間')

    @cached_property
    def clip(self):
        temp_file_path = get_tempfile('.mp4', self.file)
        return VideoFileClip(temp_file_path)

    def update_thumbnail(self, t):
        next_thumbnail_path = get_tempfile('.jpg')
        self.clip.save_frame(next_thumbnail_path, t=t)
        self.clip.close()

        with open(next_thumbnail_path, 'rb') as f:
            self.thumbnail = File(f)
            self.save()

    def update_gif(self):
        if self.duration < 3:
            return
        path = get_tempfile('.gif')

        start = random.uniform(0, self.clip.duration - 3)
        subclip = self.clip.subclip(start, start + 3).resize(0.3)

        subclip.write_gif(path, fps=12)
        subclip.close()
        self.clip.close()

        with open(path, 'rb') as f:
            self.gif = File(f)
            self.save()

    def update_file(self):
        next_file_path = get_tempfile('.mp4')
        self.clip.write_videofile(next_file_path, **settings.ENCODE_OPTIONS)
        self.clip.close()

        with open(next_file_path, 'rb') as f:
            self.file = File(f)
            self.save()

    def duration_str(self):
        hour = int((self.duration / 3600))
        minute = int((self.duration % 3600) / 60)
        second = int((self.duration % 3600) % 60)

        if hour == 0:
            hour = ''
        else:
            hour = str(hour) + ':'

        result = hour + '%02d:%02d' % (minute, second)
        return result

    def frames_count(self):
        return int(self.fps * self.duration)

    def delete(self, **kwargs):
        self.file.delete(False)
        self.thumbnail.delete(False)
        return super().delete(**kwargs)
