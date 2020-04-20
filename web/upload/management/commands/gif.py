from django.core.management.base import BaseCommand
from django.db.models import Q

from upload.models import VideoData


class Command(BaseCommand):
    def handle(self, *args, **options):
        video = VideoData.objects.filter(Q(gif__isnull=True) | Q(gif__exact=''), duration__gte=3).first()
        if video is not None:
            video.update_gif()
