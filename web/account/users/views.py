from django.shortcuts import get_object_or_404

from ..models import User
from ajax.models import Favorite
from browse.utils import safe_videos, unsafe_videos
from core.utils import AltPaginationListView


def get_tabs(n, username):
    tabs = [
        {'href': f'/u/{username}', 'title': '投稿動画', 'is_active': False},
        {'href': f'/u/{username}/favorites', 'title': 'お気に入りリスト', 'is_active': False},
        {'href': f'/u/{username}/followees', 'title': 'フォロイー', 'is_active': False},
        {'href': f'/u/{username}/followers', 'title': 'フォロワー', 'is_active': False},
    ]
    tabs[n]['is_active'] = True
    return tabs


class Profile(AltPaginationListView):
    template_name = 'users/profile.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        username = self.kwargs['username']
        if username == self.request.user.username or self.request.user.is_staff:
            return unsafe_videos().filter(user__username=username).order_by('-profile__created_at')
        return safe_videos().filter(user__username=username).order_by('-profile__created_at')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        account = get_object_or_404(User, username=self.kwargs['username'])
        context['account'] = account
        context['tabs'] = get_tabs(0, account.username)

        return context


profile = Profile.as_view()


class FavoritesList(AltPaginationListView):
    template_name = 'users/favorites.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        username = self.kwargs['username']
        return safe_videos().filter(favorite__user__username=username).order_by('-favorite__created_at')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        account = get_object_or_404(User, username=self.kwargs['username'])
        context['account'] = account
        context['tabs'] = get_tabs(1, account.username)

        return context


favorites_list = FavoritesList.as_view()


class FolloweesList(AltPaginationListView):
    template_name = 'users/followees.html'
    context_object_name = 'accounts'
    paginate_by = 9

    def get_queryset(self):
        username = self.kwargs['username']
        return User.objects.filter(follower_friendships__user__username=username)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        account = get_object_or_404(User, username=self.kwargs['username'])
        context['account'] = account
        context['tabs'] = get_tabs(2, account.username)

        return context


followees_list = FolloweesList.as_view()

class FollowersList(AltPaginationListView):
    template_name = 'users/followers.html'
    context_object_name = 'accounts'
    paginate_by = 9

    def get_queryset(self):
        username = self.kwargs['username']
        return User.objects.filter(followee_friendships__followee__username=username)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        account = get_object_or_404(User, username=self.kwargs['username'])
        context['account'] = account
        context['tabs'] = get_tabs(3, account.username)

        return context


followers_list = FollowersList.as_view()
