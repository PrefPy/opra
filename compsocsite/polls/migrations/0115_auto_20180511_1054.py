# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-05-11 15:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0114_auto_20180306_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='utility',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='question',
            name='utility_model_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
