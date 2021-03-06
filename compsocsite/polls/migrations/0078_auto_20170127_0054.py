# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-27 05:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0077_uservoterecord_initial_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_string', models.CharField(default='', max_length=500)),
                ('mov_string', models.CharField(default='', max_length=200)),
                ('node_string', models.CharField(default='', max_length=400)),
                ('edge_string', models.CharField(default='', max_length=400)),
                ('cand_num', models.IntegerField(default=1)),
                ('timestamp', models.DateTimeField(verbose_name='result timestamp')),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='polls.Question')),
            ],
        ),
        migrations.RemoveField(
            model_name='currentresult',
            name='question',
        ),
        migrations.DeleteModel(
            name='CurrentResult',
        ),
    ]
