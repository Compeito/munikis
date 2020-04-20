import traceback

from django.conf import settings
from django.core.mail import send_mail
from upload.models import UploadedPureVideo
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        pure = UploadedPureVideo.objects.first()
        if pure.is_encoding:
            return

        try:
            pure.make()
            pure.delete()
        except:
            pure.is_failed = True
            pure.traceback = traceback.format_exc()
            pure.save()

            if not settings.DEBUG:
                send_mail(
                    subject='エンコード中のエラー通知',
                    message=f'{pure.traceback}\nhttps://tsukuriga.net/admin/upload/uploadedpurevideo/{pure.id}/change/',
                    from_email=settings.SERVER_EMAIL,
                    recipient_list=[email for name, email in settings.ADMINS]
                )
