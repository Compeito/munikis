# Generated by Django 2.1.8 on 2019-04-14 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0004_notification_sender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user',
            new_name='recipient',
        ),
    ]