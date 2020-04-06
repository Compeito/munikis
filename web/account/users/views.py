from django.shortcuts import get_object_or_404

from ..models import User
from browse.utils import safe_videos, unsafe_videos
from core.utils import AltPaginationListView


class UserMixin:
    account: User = None
    tab_index = 0

    def get(self, request, *args, **kwargs):
        self.account = get_object_or_404(User, username=self.kwargs['username'])
        return super().get(request, *args, **kwargs)

    def get_tabs(self):
        account = self.account
        tabs = [
            {'href': f'/u/{account.username}', 'title': '投稿動画', 'is_active': False},
            {'href': f'/u/{account.username}/favorites', 'title': 'お気に入りリスト', 'is_active': False},
            {'href': f'/u/{account.username}/followees', 'title': f'フォロイー', 'is_active': False},
            {'href': f'/u/{account.username}/followers', 'title': f'フォロワー', 'is_active': False},
        ]
        tabs[self.tab_index]['is_active'] = True
        return tabs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['account'] = self.account
        context['tabs'] = self.get_tabs()
        return context


class Profile(UserMixin, AltPaginationListView):
    template_name = 'users/profile.html'
    context_object_name = 'videos'
    paginate_by = 12
    tab_index = 0

    def get_queryset(self):
        if self.account == self.request.user or self.request.user.is_staff:
            return unsafe_videos().filter(user=self.account).order_by('-profile__created_at')
        return safe_videos().filter(user=self.account).order_by('-profile__created_at')


profile = Profile.as_view()


class FavoritesList(UserMixin, AltPaginationListView):
    template_name = 'users/favorites.html'
    context_object_name = 'videos'
    paginate_by = 12
    tab_index = 1

    def get_queryset(self):
        return safe_videos().filter(favorite__user=self.account).order_by('-favorite__created_at')


favorites_list = FavoritesList.as_view()


class FolloweesList(UserMixin, AltPaginationListView):
    template_name = 'users/followees.html'
    context_object_name = 'accounts'
    paginate_by = 9
    tab_index = 2

    def get_queryset(self):
        return User.objects.filter(followers=self.account)


followees_list = FolloweesList.as_view()


class FollowersList(UserMixin, AltPaginationListView):
    template_name = 'users/followers.html'
    context_object_name = 'accounts'
    paginate_by = 9
    tab_index = 3

    def get_queryset(self):
        return User.objects.filter(followees=self.account)


followers_list = FollowersList.as_view()
