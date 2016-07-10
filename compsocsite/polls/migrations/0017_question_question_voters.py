# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 19:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0016_remove_question_question_voters'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_voters',
            field=models.ManyToManyField(related_name='voters', to=settings.AUTH_USER_MODEL),
        ),
    ]
