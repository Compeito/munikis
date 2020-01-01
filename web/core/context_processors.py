import json
import urllib.parse

import re
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http.request import HttpRequest
from django.utils import timezone

from account.models import User
from upload.models import Video


def query_resolver(request):
    """paginationと検索クエリなど他パラメータとの競合を解決する"""
    queries = '?'
    for k, v in dict(request.GET).items():
        if not k == 'page':
            queries += f'{k}={urllib.parse.quote(v[0])}&'
    return {'queries': queries}


def user_agent_detect(request):
    ua = request.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META.keys() else ''
    return {
        'is_ios': len(re.findall('(iphone|ipad|ipod)', ua, re.I)) > 0
    }


def admin_chart(request: HttpRequest):
    if not request.path == '/admin/':
        return {'chart_data': {}}

    def merge_dict(x: dict, y: dict):
        z = x.copy()
        z.update(y)
        return z

    # dateオブジェクトで最初の日(ユーザーと動画で古い方)から今日までキーが日付/値が0のデータを用意し、
    # 実際のデータがある日をその数値で上書きする -> データがない日を0埋めする
    first_day = min(Video.objects.first().profile.created_at, User.objects.first().date_joined).date()
    empty_data_days = {}
    for days in range((timezone.now().date() - first_day).days):
        empty_data_days[first_day + timezone.timedelta(days=days)] = 0

    video_data = (
        Video.objects.annotate(date=TruncDate("profile__created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")
    )
    video_data_dict = merge_dict(empty_data_days, {date['date']: date['count'] for date in video_data})

    user_data = (
        User.objects.annotate(date=TruncDate("date_joined"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("-date")
    )
    user_data_dict = merge_dict(empty_data_days, {data['date']: data['count'] for data in user_data})

    chart_data = {
        'video': [
            {
                'date': timezone.datetime.fromordinal(date.toordinal()),
                'y': count
            } for date, count in video_data_dict.items()
        ],
        'user': [
            {
                'date': timezone.datetime.fromordinal(date.toordinal()),
                'y': count
            } for date, count in user_data_dict.items()
        ],
    }

    return {
        'chart_data': json.dumps(chart_data, cls=DjangoJSONEncoder),
    }


def common(request):
    return {
        'DEBUG': settings.DEBUG,
        **query_resolver(request),
        **user_agent_detect(request),
        **admin_chart(request)
    }
