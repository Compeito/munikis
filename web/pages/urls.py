from django.urls import path
from . import views

app_name = 'pages'
urlpatterns = [
    path('', views.pages_list),
    path('/<slug:slug>', views.show_page, name='show'),
]
