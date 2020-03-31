from django.db import models
from django.utils import timezone

import re

from markdownx.models import MarkdownxField
from core.utils import CustomModel
from .utils import markdownify


class Page(CustomModel):
    class Categories(models.TextChoices):
        news = 'news', 'お知らせ'
        update = 'update', '更新情報'
        learn = 'learn', '学び'
        info = 'info', 'サービス情報'

    author = models.ForeignKey('account.User', verbose_name='筆者', null=True,
                               on_delete=models.SET_NULL, limit_choices_to={'is_staff': True})
    title = models.CharField('タイトル', max_length=255)
    text = MarkdownxField('本文')
    category = models.SlugField('カテゴリ', default=Categories.news, choices=Categories.choices)
    slug = models.SlugField('スラッグ')
    featured_order = models.PositiveSmallIntegerField('トップ表示順', default=0)
    is_published = models.BooleanField('公開する', default=True)

    @property
    def body(self):
        return markdownify(self.text)

    @property
    def description(self):
        result = ''
        for p in re.findall(r'<p>(.+?)</p>', self.body.replace('\n', '')):
            result += re.sub('<.+?>', '', p)
        return result[:80]

    @property
    def is_new(self):
        return (timezone.now() - self.created_at).days < 7

    @property
    def date_str(self):
        return self.created_at.strftime('%m/%d')

    @property
    def ogp_image(self):
        img = re.search(r'!\[.*\]\((?P<uri>.+)\)', self.text)
        if img:
            return img.group('uri')
        return 'https://tsukuriga.net/assets/images/ogp.png'

    def __str__(self):
        return self.title
