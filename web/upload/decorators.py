from django.shortcuts import get_object_or_404, redirect
from django.http.response import HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone

from .models import Video


def users_video_required(view):
    def wrapper(request, slug, *args, **kwargs):
        video = get_object_or_404(Video, slug=slug)
        if not video.user == request.user:
            return HttpResponseBadRequest('ユーザー情報が投稿者と一致しません')
        request.video = video
        return view(request, slug, *args, **kwargs)

    return wrapper


def upload_limitation(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_uploadable:
            localdate_uploadble = timezone.localtime(request.user.date_uploadable)
            localdate_uploadble_str = localdate_uploadble.strftime('%Y/%m/%d %H:%M:%S')
            messages.error(request, f'新規アカウントは連続投稿が制限されています。{localdate_uploadble_str}までお待ち下さい')
            return redirect('/')
        return view(request, *args, **kwargs)

    return wrapper
