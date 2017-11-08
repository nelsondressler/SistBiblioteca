# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-07 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuario',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AddField(
            model_name='usuario',
            name='username',
            field=models.CharField(default=1, max_length=50, unique=True),
            preserve_default=False,
        ),
    ]