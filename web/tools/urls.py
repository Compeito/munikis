from django.urls import path
from . import views

urlpatterns = [
    path('chat', views.Chat.as_view()),
    path('archive', views.Archive.as_view()),
    path('para/encode', views.para_encoding),
    path('para/auth', views.para_authentication),
    path('para/callback', views.para_callback),
    path('para/tweet', views.para_tweet),
    path('statistics/csv', views.statistics_csv),
]
