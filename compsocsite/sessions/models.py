from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Session(models.Model):
    creator = models.OneToOneField(User)
    admins = models.ManyToManyField(User)
    participants = models.ManyToManyField(User)
    