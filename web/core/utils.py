import re
import html
import math

from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import generic
from django.conf import settings
from django.template.defaultfilters import linebreaks

from maintenance_mode.backends import AbstractStateBackend
from maintenance_mode.io import read_file, write_file

from account.validators import username_regex


class AltPaginationListView(generic.ListView):
    paginate_range = 2

    def paginate_queryset(self, queryset, page_size):
        # (paginator, page, page.object_list, page.has_other_pages())
        paginator, page, page_objs, has_other_pages = super().paginate_queryset(queryset, page_size)

        prev_range = page.number - self.paginate_range
        if prev_range < 1:
            prev_range = 1

        next_range = page.number + self.paginate_range
        if next_range > paginator.num_pages:
            next_range = paginator.num_pages

        if page.number > self.paginate_range + 1:
            paginator.has_prev_dots = True

        if paginator.num_pages - page.number > self.paginate_range:
            paginator.has_next_dots = True

        # 結果をalt_page_rangeとして代入
        paginator.alt_page_range = range(prev_range, next_range + 1)
        return paginator, page, page_objs, has_other_pages


def created_at2str(datetime_obj):
    def mf2str(division):
        return str(math.floor(division))

    elapsed = timezone.now() - datetime_obj
    if elapsed.days >= 365:
        return mf2str(elapsed.days / 365) + '年前'
    elif elapsed.days >= 1:
        return mf2str(elapsed.days) + '日前'
    elif elapsed.seconds >= 60 * 60:
        return mf2str(elapsed.seconds / 60 / 60) + '時間前'
    elif elapsed.seconds >= 60:
        return mf2str(elapsed.seconds / 60) + '分前'
    else:
        return str(elapsed.seconds) + '秒前'


def ts2datetime(timestamp):
    return timezone.datetime.fromtimestamp(int(timestamp), tz=timezone.utc)


def get_tweet_url(tweet):
    return f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'


def gen_unique_slug(x, obj, slug_name='slug'):
    already_ids = [getattr(i, slug_name) for i in obj.objects.all()]
    while True:
        id_str = get_random_string(x)
        if id_str not in already_ids:
            return id_str


class CustomModel(models.Model):
    created_at = models.DateTimeField('作成日', default=timezone.now)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    class Meta:
        abstract = True


class LocalFileBackend(AbstractStateBackend):
    """デフォルトのLocalFileBackendの各メソッドのvalueに.strip()を追加しただけのもの"""

    def get_value(self):
        value = read_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, '0')
        if value.strip() not in ['0', '1']:
            raise ValueError('state file content value is not 0|1')
        value = bool(int(value))
        return value

    def set_value(self, value):
        value = str(int(value))
        if value.strip() not in ['0', '1']:
            raise ValueError('state file content value is not 0|1')
        write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, value)


def activate_url_from(text):
    if not text:
        return text
    result = html.escape(text)
    result = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', result)
    result = re.sub(r'(\A|\s)#(\S+)', r'<a href="/search?q=%23\2">#\2</a>', result)
    result = re.sub(rf'(\A|\s)@({username_regex})', r'<a href="/u/\2">@\2</a>', result)
    result = linebreaks(result)
    return result
