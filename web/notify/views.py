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
                .prefetch_related('sender', 'target', 'target__video', 'target__user')
                .filter(recipient=self.request.user)
                .order_by('-created_at')
        )
        return [n for n in notifications if n.target]


notifications_list = login_required(NotificationListView.as_view())
