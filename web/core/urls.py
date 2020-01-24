from django.urls import path

from . import views

urlpatterns = [
    path('watch/<slug:slug>', views.watch),
    path('edit/<slug:slug>', views.edit),
    path('thumbnail/<slug:slug>', views.edit_thumbnail),
    path('delete/<slug:slug>', views.delete),
    path('embed/<slug:slug>', views.embed),
    path('framebyframe', views.framebyframe),
]
