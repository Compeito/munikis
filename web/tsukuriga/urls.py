"""tsukuriga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from .sitemap import *

sitemaps = {
    'static': StaticViewSitemap,
    'video': VideoSitemap,
    'label': LabelSitemap,
    'page': PageSitemap,
    'user': UserSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('', include('account.urls')),
    path('pages', include('pages.urls')),
    path('markdownx/', include('markdownx.urls')),
    path('', include('social_django.urls', namespace='social')),
    path('', include('core.urls')),
    path('', include('browse.urls')),
    path('', include('tools.urls')),
    path('upload', include('upload.urls')),
    path('notify', include('notify.urls')),
    path('ajax/', include('ajax.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
