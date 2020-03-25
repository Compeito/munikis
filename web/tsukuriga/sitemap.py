from django.contrib import sitemaps

from upload.models import Video
from browse.utils import safe_videos
from browse.models import Label
from pages.models import Page
from account.models import User


class VideoSitemap(sitemaps.Sitemap):
    changefreq = 'monthly'
    priority = 1.0

    def items(self):
        return safe_videos().order_by('-published_at')

    def lastmod(self, obj: Video):
        return obj.published_at

    def location(self, obj: Video):
        return f'/watch/{obj.slug}'


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return ['/', '/pages', '/ranking']

    def location(self, item):
        return item


class LabelSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        return Label.objects.all()

    def location(self, obj: Label):
        return f'/label/{obj.slug}'


class PageSitemap(sitemaps.Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Page.objects.filter(is_published=True).order_by('created_at')

    def lastmod(self, obj: Page):
        return obj.updated_at

    def location(self, obj: Page):
        return f'/pages/{obj.slug}'


class UserSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        return User.objects.all().order_by('-date_joined')

    def lastmod(self, obj: User):
        try:
            return safe_videos().filter(user=obj).order_by('-published_at').first().published_at
        except:
            return obj.date_joined

    def location(self, obj: User):
        return f'/u/{obj.username}'
