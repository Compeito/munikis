from account.models import User
from upload.models import Video


def safe_videos(user: User = None):
    videos = (
        Video.objects
            .prefetch_related('user', 'profile', 'data', 'point_set', 'favorite_set', 'comment_set')
            .filter(
                is_ban=False,
                profile__release_type='published',
                profile__isnull=False,
                data__isnull=False
            )
    )
    if user is not None and user.is_authenticated:
        videos = videos.exclude(user__in=user.mutes.all())
    return videos


def unsafe_videos():
    return (
        Video.objects
            .prefetch_related('user', 'profile', 'data', 'point_set', 'favorite_set', 'comment_set')
            .filter(profile__isnull=False)
    )
