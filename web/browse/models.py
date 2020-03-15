from datetime import datetime
from math import sqrt, floor

from django.db import models
from django.http.response import Http404
from django.utils import timezone

from ajax.models import Comment, Point


class Ranking(models.Model):
    class DayChoices(models.TextChoices):
        day = 'day', '24時間'
        week = 'week', '週間'
        month = 'month', '月間'
        all = 'all', '全期間'

    class TypeChoices(models.TextChoices):
        popular = 'popular', '人気順'
        favorites = 'favorites', 'お気に入り順'

    point = models.IntegerField('算出ポイント', default=0)
    video = models.ForeignKey('upload.Video', verbose_name='動画', on_delete=models.CASCADE)
    day = models.CharField('期間(日)', default=1, max_length=20, choices=DayChoices.choices)
    type = models.CharField('集計タイプ', default='popular', max_length=20, choices=TypeChoices.choices)

    @staticmethod
    def raise_http404_for_sort(t, d):
        type_labels = [v for v, k in Ranking.TypeChoices.choices]
        day_labels = [v for v, k in Ranking.DayChoices.choices]
        if t not in type_labels or d not in day_labels:
            raise Http404

    @property
    def day_count(self):
        counts = {
            self.DayChoices.day: 1,
            self.DayChoices.week: 7,
            self.DayChoices.month: 30,
            self.DayChoices.all: -1,
        }
        return counts[self.day]

    @property
    def from_datetime(self):
        if self.day_count > 0:
            return timezone.now() - timezone.timedelta(self.day_count)
        return datetime(year=2019, month=4, day=1, tzinfo=timezone.now().tzinfo)

    def calculate(self):
        calculator = self.get_calculator()
        self.point = calculator()

    def get_calculator(self):
        calculator_name = f'calc_{self.type}'
        if hasattr(self, calculator_name):
            return getattr(self, calculator_name)
        raise NotImplementedError(calculator_name + 'メソッドが定義されていません')

    def calc_favorites(self):
        return self.video.favorite_set.filter(created_at__gte=self.from_datetime).count()

    def calc_popular(self):
        """
        評価指標(星、再生数、コメント、お気に入り)それぞれの性質に応じた値をもとに、評価関数にあてはめて算出した計算結果。
        現在の評価関数は((星+再生数)×コメント)+(お気に入り×お気に入り×10)
        """
        fav = self.calc_favorites()
        star = self.score_of_stars()
        view = self.score_of_views()
        comment = self.score_of_comments()
        return ((star + view) * comment) + (fav * fav * 10)

    def score_of_stars(self):
        """
        動画に対してユーザーがつけた星の数をユーザーごとにそれぞれ1/2乗し、全てのユーザーについてそれらを合計した値。
        ただし集計期間外につけられた星は算出対象から除外する。
        """
        users = []
        ip_list = []
        stars = Point.objects.filter(video=self.video, created_at__gte=self.from_datetime)
        for star in stars:
            if star.user:
                users.append(star.user)
            else:
                ip_list.append(star.ip)
        users = list(set(users))
        ip_list = list(set(ip_list))
        return self.sum_of_sqrt_star_login(stars, users) + self.sum_of_sqrt_star_anonymous(stars, ip_list)

    def sum_of_sqrt_star_login(self, stars, users):
        result = 0
        for user in users:
            users_stars = stars.filter(user=user)
            users_star_sum = 0
            for users_star in users_stars:
                users_star_sum += users_star.count
            result += floor(sqrt(users_star_sum))
        return result

    def sum_of_sqrt_star_anonymous(self, stars, ip_list):
        result = 0
        for ip in ip_list:
            ips_stars = stars.filter(ip=ip)
            ips_star_sum = 0
            for ips_star in ips_stars:
                ips_star_sum += ips_star.count
            result += floor(sqrt(ips_star_sum))
        return result

    def score_of_views(self):
        """
        現時点では動画の公開日時が集計期間内であれば再生数の値、そうでなければ0としての値。
        その1/2乗。
        """
        result = 0
        if self.from_datetime < self.video.published_at:
            result = self.video.views_count
        return sqrt(result)

    def score_of_comments(self):
        """
        集計期間内に動画に対してコメントをつけた人数の値+1。
        """
        users = []
        comments = Comment.objects.filter(video=self.video, created_at__gte=self.from_datetime)
        for comment in comments:
            users.append(comment.user)
        return len(list(set(users))) + 1


class Label(models.Model):
    COLOR_SET = (
        ("orange", "orange"),
        ("yellow", "yellow"),
        ("green", "green"),
        ("turqoise", "turqoise"),
        ("cyan", "cyan"),
        ("blue", "blue"),
        ("purple", "purple"),
        ("red", "red"),
        ("pink", "pink"),
        ("grey", "grey"),
        ("grey-light", "grey-light"),
        ("grey-lighter", "grey-lighter"),
    )
    slug = models.SlugField('スラッグ')
    color = models.CharField('色', max_length=20, choices=COLOR_SET)
    title = models.CharField('タイトル', max_length=50)
    description = models.TextField('説明')
    is_active = models.BooleanField('アクティブ', default=True)

    @property
    def css_classes(self):
        return f'tag is-rounded is-{self.color}'

    @property
    def safe_videos_count(self):
        # 循環インポートが発生するため
        from browse.utils import safe_videos
        return safe_videos().filter(profile__labels=self).count()

    def __str__(self):
        return self.title


class VideoProfileLabelRelation(models.Model):
    profile = models.ForeignKey('upload.VideoProfile', on_delete=models.CASCADE)
    label = models.ForeignKey(Label, null=True, blank=True, on_delete=models.CASCADE)
