import functools
import operator
import re
import twitter
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST

from account.models import User
from ajax.forms import CommentForm, AddPointForm
from browse.utils import safe_videos
from upload.decorators import users_video_required
from upload.generic import VideoProfileUpdateView
from upload.importer import TwitterImporter, ImportFileError
from upload.models import Video
from .forms import ThumbnailForm, DeleteVideoForm


def watch(request, slug):
    video = get_object_or_404(Video, slug=slug)

    if not video.user == request.user and video.profile.release_type == 'unpublished':
        raise Http404

    label_videos = []
    labels = video.profile.labels.all()
    if labels.exists():
        label_videos = safe_videos().filter(
            functools.reduce(operator.or_, (Q(profile__labels=label) for label in labels))
        ).order_by('?')[:10]
    # 不足分をランダムで補填
    random_videos = safe_videos().order_by('?')[:10 - len(label_videos)]
    related_videos = list(label_videos) + list(random_videos)

    video.views_count += 1
    video.save()

    if video.is_failed and video.user == request.user:
        messages.error(request, 'エンコード処理が正常に終了しませんでした。しばらく時間をおいてから、動画を削除して再投稿してみてください')

    if video.is_ban:
        messages.error(request, 'この動画は運営によって非公開に設定されました。投稿者以外は閲覧できません')

    return render(request, 'core/watch.html', {'video': video, 'related_videos': related_videos, 'form': CommentForm(),
                                               'modal_form': AddPointForm()})


class Edit(VideoProfileUpdateView):
    template_name = 'core/edit.html'

    def get_success_url(self):
        return f'/watch/{self.request.video.slug}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['video'] = self.request.video
        context['modal_form'] = DeleteVideoForm()
        return context


@login_required
@users_video_required
def edit(request, slug):
    return Edit.as_view()(request, slug)


@login_required
@users_video_required
def edit_thumbnail(request, slug):
    video = request.video
    if not video.is_encoded:
        messages.error(request, 'エンコードが完了するまでは利用できません')
        return redirect(f'/edit/{video.slug}')

    form = ThumbnailForm()

    if request.method == 'POST':
        form = ThumbnailForm(request.POST)

        if form.is_valid():
            t = form.cleaned_data['time']

            if 0 <= t <= video.data.duration:
                try:
                    video.data.update_thumbnail(t=t)
                    messages.success(request, '変更されました')
                    return redirect(f'/watch/{video.slug}')
                except OSError:
                    messages.error(request, 'サムネイルの変更に失敗しました')

            else:
                messages.error(request, '指定した秒数が不正です')

    return render(request, 'core/thumbnail.html', {'video': video, 'form': form})


@require_POST
@login_required
@users_video_required
def delete(request, slug):
    video = request.video
    form = DeleteVideoForm(request.POST)

    if form.is_valid():
        if form.cleaned_data['slug'] == video.slug:
            video.delete()
            messages.success(request, '削除しました')
            return redirect(f'/u/{request.user.username}')

    messages.error(request, '送信した値が不正です')
    return redirect(f'/edit/{slug}')


@xframe_options_exempt
def embed(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return render(request, 'core/embed.html', {'video': video})


def framebyframe(request):
    url = request.GET.get('url', '')
    twitter_matched = re.search(TwitterImporter.pattern, url)
    media_matched = re.search(r'https://storage\.tsukuriga\.net/altwug/.+/movie\.mp4', url)

    file_url = ''
    thumbnail_url = 'https://tsukuriga.net/assets/images/ogp.png'
    if twitter_matched:
        tweet_id = twitter_matched.group('id')
        admin_user: User = User.objects.filter(is_staff=True).first()
        try:
            tweet = admin_user.api.GetStatus(tweet_id)
            file_url = TwitterImporter.get_video_url(tweet)
        except twitter.error.TwitterError as e:
            messages.error(request, 'ツイートの取得に失敗ました')
        except ImportFileError as e:
            messages.error(request, str(e))
    elif media_matched:
        file_url = url
    elif url:
        messages.error(request, 'URLの形式が不正です')

    data = {
        'file': {'url': file_url},
        'thumbnail': {'url': thumbnail_url}
    }
    return render(request, 'core/framebyframe.html', {'video': {'data': data}})
