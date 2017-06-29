from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Session(models.Model):
    title = models.TextField()
    description = models.TextField()
    creator = models.OneToOneField(User)
    admins = models.ManyToManyField(User)
    participants = models.ManyToManyField(User,related_name='sessions_participated')
    link = models.TextField(default="")
    pub_date = models.DateTimeField('date published')