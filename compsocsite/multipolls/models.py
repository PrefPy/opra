from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.conf import settings
from polls.models import *
from groups.models import *
# Create your models here.

@python_2_unicode_compatible
class MultiPoll(models.Model):
    number = models.IntegerField(default=1)
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    owner = models.ForeignKey(User,related_name='owner')
    questions = models.ManyToManyField(Question, through='MultiPollQuestion', through_fields=('multipoll','question'),)
    voters = models.ManyToManyField(User)
    pos = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    #pub_date = models.DateTimeField('date published')
    def __str__(self):
        return ""

@python_2_unicode_compatible
class MultiPollQuestion(models.Model):
    class Meta:
        ordering = ['order']
    multipoll = models.ForeignKey(MultiPoll)
    question = models.ForeignKey(Question)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return ""
    

