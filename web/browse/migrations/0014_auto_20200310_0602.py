# Generated by Django 2.1.15 on 2020-03-10 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('browse', '0013_label_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='label',
            name='color',
            field=models.CharField(choices=[('orange', 'orange'), ('yellow', 'yellow'), ('green', 'green'), ('turqoise', 'turqoise'), ('cyan', 'cyan'), ('blue', 'blue'), ('purple', 'purple'), ('red', 'red'), ('pink', 'pink'), ('grey', 'grey'), ('grey-light', 'grey-light'), ('grey-lighter', 'grey-lighter')], max_length=20, verbose_name='色'),
        ),
    ]