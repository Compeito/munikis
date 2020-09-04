from django.urls import path
from django.http.response import HttpResponse

from . import views


def closed(request):
    return HttpResponse('このページは現在利用できません')


urlpatterns = [
    path('chat', closed),
    path('archive', closed),
    path('para/encode', views.para_encoding),
    path('para/auth', views.para_authentication),
    path('para/callback', views.para_callback),
    path('para/tweet', views.para_tweet),
    path('statistics/csv', views.statistics_csv),
    path('job/<str:command>', views.job_endpoint),
]
