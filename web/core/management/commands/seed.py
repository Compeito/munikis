import os.path
import random
from typing import List

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from account.models import User
from ajax.models import Comment, Point, Favorite
from browse.models import Label, VideoProfileLabelRelation
from notify.models import Notification
from pages.models import Page
from upload.models import Video, VideoProfile, VideoData


class Command(BaseCommand):
    help: str = '初期データを作成するコマンド'
    used_username: List[str] = []
    used_slug: List[str] = []

    @staticmethod
    def random_bool() -> bool:
        return random.randint(0, 1) == 0

    def unique_username(self) -> str:
        while True:
            username = self.fake.profile()['username'][:20]
            if username not in self.used_username:
                self.used_username.append(username)
                return username

    def unique_slug(self) -> str:
        while True:
            slug = Faker().slug()
            if slug not in self.used_slug:
                self.used_slug.append(slug)
                return slug

    @property
    def fake(self) -> Faker:
        return Faker('ja_JP')

    def handle(self, *args, **options) -> None:
        test_user = User.objects.create_superuser(
            username='test',
            email='test@example.com',
            password='test',
            name='test',
        )
        print(f'管理者ユーザー作成')

        fake_users = []
        for i in range(20):
            fake_profile = self.fake.profile()
            fake_user = User(
                username=self.unique_username(),
                name=fake_profile['name'],
                description=self.fake.text(),
                is_accept_mail=self.random_bool(),
                contribution_point=random.randint(100, 1000)
            )
            fake_users.append(fake_user)
            print(f'ユーザー作成...{i + 1}')
        User.objects.bulk_create(fake_users)
        print(f'ユーザー作成完了')

        fake_labels = []
        for i in range(10):
            fake_label = Label(
                slug=self.unique_slug(),
                color=random.choice(Label.COLOR_SET)[0],
                title=self.fake.word(),
                description=self.fake.sentence()
            )
            fake_labels.append(fake_label)
            print(f'ラベル作成...{i + 1}')
        Label.objects.bulk_create(fake_labels)
        print(f'ラベル作成完了')

        fake_videos = []
        fake_profiles = []
        fake_vpl_rels = []
        fake_datas = []
        fake_comments = []
        fake_points = []
        fake_favorites = []
        movie = open(os.path.join(settings.BASE_DIR, 'seeds', 'movie.mp4'), 'rb')
        thumbnail = open(os.path.join(settings.BASE_DIR, 'seeds', 'thumbnail.jpg'), 'rb')
        gif = open(os.path.join(settings.BASE_DIR, 'seeds', 'thumbnail.gif'), 'rb')
        for i in range(70):
            fake_video = Video(
                user_id=1 if i < 49 else i - 48,
                is_pickup=self.random_bool(),
                published_at=timezone.now(),
                views_count=random.randint(0, 1000),
                type=random.choice(Video.VIDEO_TYPES)[0]
            )
            fake_videos.append(fake_video)
            print(f'動画作成...{i + 1}')

            fake_profile = VideoProfile(
                video_id=i + 1,
                release_type='published',
                title=self.fake.sentence(),
                description=self.fake.text(),
                is_loop=self.random_bool(),
                allows_anonymous_comment=self.random_bool(),
            )
            fake_profiles.append(fake_profile)

            fake_vpl_rel = VideoProfileLabelRelation(
                profile_id=i + 1,
                label_id=random.randint(1, 10),
            )
            fake_vpl_rels.append(fake_vpl_rel)

            fake_data = VideoData(
                video_id=i + 1,
                file=File(movie),
                thumbnail=File(thumbnail),
                gif=File(gif),
                fps=random.randint(1, 30),
                duration=random.randint(1, 1000) / 10
            )
            fake_datas.append(fake_data)

            for j in range(5):
                fake_comment = Comment(
                    user_id=random.randint(1, 20),
                    video_id=i + 1,
                    is_anonymous=self.random_bool(),
                    text=self.fake.text()[:150],
                )
                fake_comments.append(fake_comment)

                fake_point = Point(
                    user_id=random.randint(1, 20),
                    video_id=i + 1,
                    ip=self.fake.ipv4(),
                    count=random.randint(1, 1000)
                )
                fake_points.append(fake_point)

                fake_favorite = Favorite(
                    user_id=random.randint(1, 20),
                    video_id=i + 1,
                )
                fake_favorites.append(fake_favorite)
                print(f'評価...{j + 1}')

        Video.objects.bulk_create(fake_videos)
        VideoProfile.objects.bulk_create(fake_profiles)
        VideoProfileLabelRelation.objects.bulk_create(fake_vpl_rels)
        VideoData.objects.bulk_create(fake_datas)
        print('動画作成完了')

        Comment.objects.bulk_create(fake_comments)
        Point.objects.bulk_create(fake_points)
        Favorite.objects.bulk_create(fake_favorites)
        print('評価データ作成完了')

        movie.close()
        thumbnail.close()
        gif.close()

        fake_pages = []
        for i in range(20):
            fake_page = Page(
                author=test_user,
                title=self.fake.sentence(),
                text=self.fake.text(),
                slug=self.unique_slug(),
                featured_order=random.choice([0, 0, 0, 1])
            )
            fake_pages.append(fake_page)
            print(f'記事...{i + 1}')
        Page.objects.bulk_create(fake_pages)
        print('記事作成完了')

        fake_notifications = []
        for i in range(20):
            if random.randint(0, 1) == 1:
                target = Comment.objects.order_by('?').first()
            else:
                target = Favorite.objects.order_by('?').first()
            fake_notification = Notification(
                recipient_id=1,
                sender_id=i + 1,
                target=target
            )
            fake_notifications.append(fake_notification)
            print(f'通知作成...{i + 1}')
        Notification.objects.bulk_create(fake_notifications)
        print('通知作成完了')
