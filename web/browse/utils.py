from upload.models import Video


def safe_videos():
    return (
        Video.objects
            .prefetch_related('user', 'profile', 'data', 'point_set', 'favorite_set')
            .filter(
                is_ban=False,
                profile__release_type='published',
                profile__isnull=False,
                data__isnull=False
            )
    )
