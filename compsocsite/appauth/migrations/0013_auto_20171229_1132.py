# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-29 16:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('appauth', '0012_auto_20171224_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='time_creation',
            field=models.DateTimeField(verbose_name=datetime.datetime(2017, 12, 29, 16, 32, 26, 643080, tzinfo=utc)),
        ),
    ]
