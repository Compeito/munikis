from django.urls import path, include

from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.CustomLoginView.as_view()),
    path('logout', views.CustomLogoutView.as_view()),
    path('password', include('account.auth.password.urls'))
]
