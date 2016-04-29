from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
@python_2_unicode_compatible
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
    	return now - datetime.timedelta(days=1) <= self.pub_date <= now

@python_2_unicode_compatible
class Item(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	item_text = models.CharField(max_length=200)
	rank = models.IntegerField(default=0)
	def __str__(self):
		return self.item_text

@python_2_unicode_compatible
class Choice(models.Model):
    item = models.ForeignKey(Item, default=1, on_delete=models.CASCADE)
    choice_num = models.IntegerField(default=1)
    votes = models.IntegerField(default=0)
    def __str__(self):
    	return str(self.choice_num)