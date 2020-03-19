from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>', views.profile),
    path('<str:username>/favorites', views.favorites_list),
    path('<str:username>/followees', views.followees_list),
    path('<str:username>/followers', views.followers_list),
]
