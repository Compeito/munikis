from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('recent', views.recent),
    path('search', views.search),
    path('ranking', views.ranking),
    path('ranking/<slug:type>', views.ranking),
    path('ranking/<slug:type>/<slug:day>', views.ranking),
    path('label', views.label_index),
    path('label/<slug:slug>', views.label),
]
