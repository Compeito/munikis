from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


class Notification(models.Model):
    recipient = models.ForeignKey(
        'account.User', verbose_name='受診者', on_delete=models.CASCADE, related_name='received_notifications'
    )
    sender = models.ForeignKey(
        'account.User', verbose_name='送信者', on_delete=models.CASCADE, related_name='sent_notifications',
    )
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.IntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    @property
    def is_new(self):
        is_read = self.is_read
        self.is_read = True
        self.save()
        return not is_read

    @property
    def type(self):
        return str(self.target_content_type.model)

    @property
    def sender_profile_icon_url(self):
        # 匿名コメントに対応するため
        # notification-item.html内でプロフィールアイコンのみコンポーネント化していない
        if self.type == 'comment':
            return self.target.profile_icon_url
        return self.sender.profile_icon_url

    @property
    def component_path(self):
        return f'notify/components/types/{self.type}.html'

    @property
    def mail_subject(self):
        titles = {
            'comment': f'{self.sender.name}さんがコメントしました',
            'favorite': f'{self.sender.name}さんがお気に入りリストに追加しました',
        }
        return titles[self.type]

    @property
    def mail_body(self):
        content = get_template(self.component_path).render({'target': self.target})
        body = get_template('notify/mails/base.html').render({'content': content})
        return body

    def send_mail(self):
        mail = EmailMultiAlternatives(
            subject=self.mail_subject,
            to=[self.recipient.email]
        )
        mail.attach_alternative(self.mail_body, 'text/html')
        return mail.send()

    @property
    def is_barrage(self):
        # お気に入り連打でメールが連投されることへの対策、ただしコメントなど一部オブジェクトの連投を許可
        # barrageは「弾幕」の意味
        if self.type in ['comment']:
            return False

        latest_notify = Notification.objects.filter(
            recipient=self.recipient,
            sender=self.sender
        ).order_by('-created_at').first()

        if latest_notify:
            diff = (self.created_at - latest_notify.created_at).total_seconds()
            return diff < 5 * 60
        return False

    def is_available_mail(self):
        return not settings.DEBUG and \
               self.pk is None and \
               self.recipient.is_accept_mail and \
               not self.is_barrage

    def save(self, *args, **kwargs):
        if self.is_available_mail():
            self.send_mail()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.mail_subject + ('(削除済み)' if self.target is None else '')


"""
シンプルなメッセージを送信するモデル
class Message(models.Model):
    ...
"""
