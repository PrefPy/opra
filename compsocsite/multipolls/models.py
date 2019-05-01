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
    owner = models.ForeignKey(User,related_name='owner', on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, through='MultiPollQuestion', through_fields=('multipoll','question'))
    voters = models.ManyToManyField(User, related_name='multipoll_participated')
    pos = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    emailInvite = models.BooleanField(default=True)
    emailDelete = models.BooleanField(default=True)    
    #pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.title

@python_2_unicode_compatible
class MultiPollQuestion(models.Model):
    class Meta:
        ordering = ['order']
    multipoll = models.ForeignKey(MultiPoll, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return ""
    
# a poll can have multiple dependent polls (must be part of the same multipoll)
class Combination(models.Model):
    target_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    dependent_questions = models.ManyToManyField(Question, related_name="dependent_questions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dependencies = models.ManyToManyField(Item)
    response = models.OneToOneField(Response,null=True, blank=True, on_delete=models.CASCADE)

# link the choices for the dependent polls to a response
class ConditionalItem(models.Model):
    combination = models.ForeignKey(Combination, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    response = models.ForeignKey(Response, null=True, blank=True, on_delete=models.CASCADE)