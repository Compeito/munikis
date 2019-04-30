# Generated by Django 2.1.8 on 2019-04-30 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('browse', '0004_auto_20190430_0056'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoProfileChannelRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='browse.Channel')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.VideoProfile')),
            ],
        ),
    ]
