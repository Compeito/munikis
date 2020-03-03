import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from social_core import exceptions as social_exceptions
from social_django.views import complete

from .decorators import account_create_limitation
from ..forms import SignUpForm


@account_create_limitation
def signup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'ログインしました')
            return redirect('/')
    return render(request, 'auth/signup.html', {'form': form})


def social_auth_complete(request, backend):
    try:
        return complete(request, backend)
    except ValueError as e:
        if type(e) == social_exceptions.AuthAlreadyAssociated:
            messages.error(request, 'すでに使用済みのアカウントです')
        else:
            messages.error(request, '予期せぬエラーが発生しました')
            if not settings.DEBUG:
                send_mail(
                    subject='ソーシャルログインのエラー通知',
                    message=traceback.format_exc(),
                    from_email=settings.SERVER_EMAIL,
                    recipient_list=[email for name, email in settings.ADMINS]
                )

        return redirect('/account/login')


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def get_success_url(self):
        messages.success(self.request, 'ログインしました')
        return super().get_success_url()


class CustomLogoutView(LogoutView):
    next_page = '/'

    def get_next_page(self):
        messages.success(self.request, 'ログアウトしました')
        return super().get_next_page()
