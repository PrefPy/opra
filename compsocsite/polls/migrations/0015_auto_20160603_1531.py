# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-03 19:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0014_auto_20160603_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_voters',
            field=models.ManyToManyField(related_name='voters', to=settings.AUTH_USER_MODEL),
        ),
    ]