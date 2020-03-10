import os.path
import random

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from account.models import User
from browse.models import Label, VideoProfileLabelRelation
from pages.models import Page
from upload.models import Video, VideoProfile, VideoData


class Command(BaseCommand):
    help = '初期データを作成するコマンド'
    used_username = []
    used_slug = []

    @staticmethod
    def random_bool():
        return random.randint(0, 1) == 0

    def unique_username(self):
        while True:
            username = self.fake.profile()['username'][:20]
            if username not in self.used_username:
                self.used_username.append(username)
                return username

    def unique_slug(self):
        while True:
            slug = Faker().slug()
            if slug not in self.used_slug:
                self.used_slug.append(slug)
                return slug

    @property
    def fake(self):
        return Faker('ja_JP')

    def create_video(self, user, label):
        with open(os.path.join(settings.BASE_DIR, 'seeds', 'movie.mp4'), 'rb') as movie, \
            open(os.path.join(settings.BASE_DIR, 'seeds', 'thumbnail.jpg'), 'rb') as thumbnail, \
            open(os.path.join(settings.BASE_DIR, 'seeds', 'thumbnail.gif'), 'rb') as gif:
            fake_video = Video.objects.create(
                user=user,
                is_pickup=self.random_bool(),
                published_at=timezone.now(),
                views_count=random.randint(0, 1000),
                type=random.choice(Video.VIDEO_TYPES)[0]
            )
            fake_profile = VideoProfile.objects.create(
                video=fake_video,
                release_type='published',
                title=self.fake.sentence(),
                description=self.fake.text(),
                is_loop=self.random_bool(),
                allows_anonymous_comment=self.random_bool(),
            )
            VideoProfileLabelRelation.objects.create(
                profile=fake_profile,
                label=label,
            )
            VideoData.objects.create(
                video=fake_video,
                file=File(movie),
                thumbnail=File(thumbnail),
                gif=File(gif),
                fps=random.randint(1, 30),
                duration=random.randint(1, 1000) / 10
            )

    def handle(self, *args, **options):
        test_user = User.objects.create_superuser(
            username='test',
            email='test@example.com',
            password='test',
            name='test',
        )

        fake_users = []
        for i in range(20):
            fake_profile = self.fake.profile()
            fake_user = User.objects.create(
                username=self.unique_username(),
                name=fake_profile['name'],
                description=self.fake.text(),
                is_accept_mail=self.random_bool(),
                contribution_point=random.randint(100, 1000)
            )
            fake_users.append(fake_user)

        fake_labels = [None]
        for i in range(10):
            fake_label = Label.objects.create(
                slug=self.unique_slug(),
                color=random.choice(Label.COLOR_SET)[0],
                title=self.fake.word(),
                description=self.fake.sentence()
            )
            fake_labels.append(fake_label)

        for user in fake_users:
            self.create_video(user, random.choice(fake_labels))

        for i in range(50):
            self.create_video(test_user, random.choice(fake_labels))

        for i in range(20):
            Page.objects.create(
                author=test_user,
                title=self.fake.sentence(),
                text=self.fake.text(),
                slug=self.unique_slug(),
                featured_order=random.choice([0, 0, 0, 1])
            )
