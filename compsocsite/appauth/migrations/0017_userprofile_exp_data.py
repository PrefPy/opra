# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-24 07:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appauth', '0016_userprofile_numq'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='exp_data',
            field=models.TextField(default='{}'),
        ),
    ]
