from django.contrib.auth.decorators import login_required

from core.utils import AltPaginationListView
from .models import Notification


class NotificationListView(AltPaginationListView):
    template_name = 'notify/index.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        video_notifications = (
            Notification.objects
                .select_related('target_content_type')
                .prefetch_related('sender', 'target', 'target__video', 'target__user', 'target__video__profile')
                .filter(target_content_type__model__in=('comment', 'favorite'), recipient=self.request.user)
        )
        friendship_notifications = (
            Notification.objects
                .select_related('sender', 'recipient')
                .filter(target_content_type__model='friendship', recipient=self.request.user)
        )
        # prefetch_relatedでtargetを指定しているため以下のnotificationsの各要素で
        # n.target_content_type_idなどがNoneになっておりsave出来ないため除外
        notifications = sorted(
            [n for n in video_notifications if n.target] +
            [n for n in friendship_notifications if n.target],
            key=lambda n: n.created_at, reverse=True
        )

        for n in notifications:
            n.is_new = False
            if not n.is_read:
                n.is_read = True
                n.save()
                n.is_new = True
        return notifications


notifications_list = login_required(NotificationListView.as_view())
