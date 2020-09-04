import csv
import json

import base64
import functools
import operator
import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView
from moviepy.editor import ImageSequenceClip

from ajax.utils import get_ip, get_anonymous_name
from browse.utils import safe_videos
from core.utils import AltPaginationListView
from upload.utils import get_tempfile
from .forms import PostForm, GIFEncodingForm, GIFTweetForm
from .models import Post


class Chat(CreateView):
    template_name = 'chat/index.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.ip = get_ip(self.request)
        if self.request.user.is_authenticated:
            post.user = self.request.user
        post.save()
        return redirect('/chat')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            name = str(self.request.user)
        else:
            name = get_anonymous_name(get_ip(self.request))
        kwargs['initial'] = {'name': name}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = list(Post.objects.all().order_by('-created_at')[:20])[::-1]
        return context


@require_POST
@csrf_exempt
def para_encoding(request):
    form = GIFEncodingForm(request.POST)
    if form.is_valid():
        frames_base64 = form.cleaned_data['text'].split('@')
        temp_file_list = []

        for frame in frames_base64:
            file = ContentFile(base64.b64decode(frame))
            temp_file = get_tempfile('.png', file)
            temp_file_list.append(temp_file)

        clip = ImageSequenceClip(temp_file_list, fps=form.cleaned_data['fps'])
        gif_path = get_tempfile('.gif')
        clip.write_gif(gif_path)

        with open(gif_path, 'rb') as f:
            encoded_string = base64.b64encode(f.read())

    return JsonResponse({'base64': encoded_string.decode('utf-8')})


@require_GET
def para_authentication(request):
    return JsonResponse({
        'loginPath': '/login/twitter/?next=/para/callback',
        'isAuthenticated': request.user.is_authenticated and request.user.has_twitter_auth
    })


def para_callback(request):
    return render(request, 'para/callback.html')


@require_POST
@csrf_exempt
@login_required
def para_tweet(request):
    form = GIFTweetForm(request.POST)
    if form.is_valid():
        file = ContentFile(base64.b64decode(form.cleaned_data['media']))
        media_path = get_tempfile('.gif', file)
        with open(media_path, 'rb') as f:
            try:
                request.user.api.PostUpdate(form.cleaned_data['text'], media=f)
            except:
                return JsonResponse({
                    'isTweeted': False,
                    'message': 'ツイートに失敗しました。ツクリガからログアウトしてから再度試してみてください。'
                })

        return JsonResponse({'isTweeted': True, 'message': 'ツイートに成功しました'})

    return JsonResponse({'isTweeted': False, 'message': 'ツイートに失敗しました。送信情報が不正です。'})


@staff_member_required
def statistics_csv(request):
    response = HttpResponse(content_type='text/csv', charset='utf-8_sig')
    response['Content-Disposition'] = 'attachment; filename=dump.csv'

    writer = csv.writer(response)
    columns = {
        '動画名': 'profile.title',
        '動画ID': 'slug',
        '投稿者名': 'user.name',
        '投稿者ID': 'user.username',
        '再生回数': 'views_count',
        '総スター数': 'points_count',
        '総スター人数': 'point_users_count',
        '総コメント人数': 'commentators_count',
        '総いいね数': 'favorites_count',
        '投稿日': 'published_at_str',
        '動画ファイル': 'data.file.url'
    }
    writer.writerow(columns.keys())

    q = request.GET.get('q')
    if not q:
        videos = safe_videos()
    else:
        q_list = q.split(',')

        videos = safe_videos().filter(
            functools.reduce(operator.or_, (Q(profile__title__contains=item) for item in q_list)) |
            functools.reduce(operator.or_, (Q(profile__description__contains=item) for item in q_list))
        ).order_by('-published_at')

    labels = request.GET.get('labels')
    if labels:
        label_list = labels.split(',')
        videos = videos.filter(
            functools.reduce(operator.or_, (Q(profile__labels__slug__contains=item) for item in label_list))
        ).order_by('-published_at')

    for video in videos:
        row = []
        for k, v in columns.items():
            data = operator.attrgetter(v)(video)
            row.append(str(data).replace(',', ' '))

        writer.writerow(row)

    return response


class Archive(AltPaginationListView):
    template_name = "archive/index.html"
    context_object_name = "archives"
    paginate_by = 16

    def get_queryset(self):
        response = requests.get('https://storage.googleapis.com/gcs.tsukuriga.net/altwug/dump.json')
        archives = json.loads(response.text)
        name = self.request.GET.get('name', '')
        return list(filter(lambda j: name in j['user'] or name in j['username'], archives))


def job_endpoint(request, command):
    allowed_commands = [
        'encode', 'gif', 'ranking',
        'contrib', 'ping_google', 'retweet'
    ]
    result = ''
    if command in allowed_commands:
        result = call_command(command)
    return HttpResponse(result)
