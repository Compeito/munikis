# Generated by Django 2.1.8 on 2019-04-30 12:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('upload', '0011_auto_20190430_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoprofile',
            name='labels',
            field=models.ManyToManyField(blank=True, through='browse.VideoProfileLabelRelation', to='browse.Labels',
                                         verbose_name='ラベル'),
        ),
    ]
