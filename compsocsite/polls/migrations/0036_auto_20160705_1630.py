# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-05 20:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0035_auto_20160705_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='imageFile',
            new_name='image',
        ),
    ]
