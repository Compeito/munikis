from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone

from upload.models import Video, VideoProfile
from account.models import User
from .models import Comment, Point
from .forms import CommentForm, AddPointForm
from .utils import json_response, get_ip


def login_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return json_response([{'message': 'ログインが必要です'}], status=401)
        return view(request, *args, **kwargs)

    return wrapper


@require_POST
@login_required
def add_comment(request, slug):
    video = get_object_or_404(Video, slug=slug)
    video_profile = get_object_or_404(VideoProfile, video=video)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment.is_anonymous and not video_profile.allows_anonymous_comment:
            return json_response([{'message': 'この動画に匿名のコメントは投稿できません'}], status=400)
        comment.user = request.user
        comment.video = video
        comment.save()
        return json_response([{'message': 'コメントが追加されました'}], status=200)

    return json_response(form.errors, status=400)


@require_POST
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user == comment.user:
        comment.delete()
        return json_response([{'message': 'コメントが削除されました'}], status=200)
    return json_response([{'message': 'ユーザー情報がコメントと一致しません'}], status=400)


@require_GET
def list_comments(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return json_response([c.json(request.user) for c in video.comment_set.all().order_by('-created_at')])


@require_POST
def add_point(request, slug):
    video = get_object_or_404(Video, slug=slug)
    form = AddPointForm(request.POST)

    if form.is_valid():
        if request.user.is_authenticated:
            old_point = video.point_set.filter(
                user=request.user, created_at__day=timezone.now().day
            ).first()
        else:
            old_point = video.point_set.filter(
                user__isnull=True, ip=get_ip(request), created_at__day=timezone.now().day
            ).first()

        if old_point:
            old_point.count += form.cleaned_data['count']
            old_point.save()

        else:
            Point.objects.create(
                video=video,
                user=request.user if request.user.is_authenticated else None,
                ip=get_ip(request),
                count=form.cleaned_data['count']
            )
        return json_response([{'message': '評価が送信されました！'}], status=200)

    return json_response(form.errors, status=400)


@require_GET
def list_points(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return json_response([p.json() for p in video.point_set.all().order_by('-created_at')], status=200)


@require_POST
@login_required
def toggle_favorite(request, slug):
    video = get_object_or_404(Video, slug=slug)

    old_favorites = video.favorite_set.filter(user=request.user)
    if old_favorites.exists():
        old_favorite = old_favorites.first()
        old_favorite.delete()
        message = 'お気に入りリストから削除しました'
    else:
        video.favorite_set.create(user=request.user)
        message = 'お気に入りリストに追加しました'

    return json_response({'message': message, 'isCreated': not old_favorites.exists()}, status=200)


@require_GET
def list_favorites(request, slug):
    video = get_object_or_404(Video, slug=slug)
    favorites = video.favorite_set.all().order_by('-created_at')

    is_created = False
    for favorite in favorites:
        if favorite.user == request.user:
            is_created = True

    return json_response({
        'favorites': [f.json() for f in favorites],
        'isCreated': is_created
    }, status=200)


@require_POST
@login_required
def toggle_friendship(request, username):
    if request.user.username == username:
        return json_response({'message': '自分自身をフォローできません'}, status=400)
    followee = get_object_or_404(User, username=username)

    old_friendships = request.user.followee_friendships.filter(followee=followee)
    if old_friendships.exists():
        old_friendships.first().delete()
        message = 'フォローを解除しました'
        is_following = False
    else:
        request.user.followee_friendships.create(followee=followee)
        message = 'フォローしました'
        is_following = True

    return json_response({'message': message, 'isFollowing': is_following}, status=200)


@require_GET
@login_required
def exist_friendship(request, username):
    is_following = request.user.followee_friendships.filter(
        followee__username=username
    ).exists()
    return json_response({'isFollowing': is_following}, status=200)


@require_POST
@login_required
def toggle_mute(request, username):
    if request.user.username == username:
        return json_response({'message': '自分自身をミュートできません'}, status=400)
    target = get_object_or_404(User, username=username)

    old_mute = request.user.mute_relations.filter(target=target)
    if old_mute.exists():
        old_mute.first().delete()
        message = f'@{username}のミュートを解除しました'
        is_muted = False
    else:
        request.user.mute_relations.create(target=target)
        message = f'@{username}をミュートしました'
        is_muted = True

    return json_response({'message': message, 'isMuted': is_muted}, status=200)


@require_GET
@login_required
def exist_mute(request, username):
    is_muted = request.user.mute_relations.filter(
        target__username=username
    ).exists()
    return json_response({'isMuted': is_muted}, status=200)
