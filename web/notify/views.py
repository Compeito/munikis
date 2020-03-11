from django.contrib.auth.decorators import login_required

from core.utils import AltPaginationListView
from .models import Notification


class NotificationListView(AltPaginationListView):
    template_name = 'notify/index.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        notifications = (
            Notification.objects
                .prefetch_related('sender', 'target', 'target__video', 'target__user', 'target__video__profile')
                .filter(recipient=self.request.user)
                .order_by('-created_at')
        )
        # prefetch_relatedでtargetを指定しているためか以下のnotificationsの各要素で
        # n.target_content_type_idなどがNoneになっているため、save出来ない
        notifications = [n for n in notifications if n.target]

        for n in notifications:
            n.is_new = False
            if not n.is_read:
                n.is_read = True
                n.save()
                n.is_new = True
        return notifications


notifications_list = login_required(NotificationListView.as_view())
