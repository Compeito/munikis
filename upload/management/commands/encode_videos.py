import traceback
from threading import Thread

import django
from django.core.management.base import BaseCommand
from upload.models import UploadedPureVideo


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        videos = UploadedPureVideo.objects.all().order_by('-created_at')
        for video in videos:
            if video.is_encoding:
                continue

            def target():
                django.setup()
                video.make()

            try:
                thread = Thread(target=target)
                thread.start()
                thread.join()
                video.delete()
            except:
                video.is_failed = True
                video.traceback = traceback.format_exc()
                video.save()
