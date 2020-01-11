from upload.models import Video


def safe_videos():
    return Video.objects.filter(
        is_ban=False,
        profile__release_type='published',
        profile__isnull=False,
        data__isnull=False
    )
