# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-15 02:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0071_auto_20161113_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservoterecord',
            name='device',
            field=models.CharField(default='', max_length=20),
        ),
    ]
