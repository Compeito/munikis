import json
import urllib.parse

import re
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
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

    week_ago = timezone.now() - timezone.timedelta(days=7)
    chart_data = {
        'video': list(
            Video.objects.filter(profile__created_at__gte=week_ago)
                .annotate(date=TruncDay("profile__created_at"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        ),
        'user': list(
            User.objects.filter(date_joined__gte=week_ago)
                .annotate(date=TruncDay("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )
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
