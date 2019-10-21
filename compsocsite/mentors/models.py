from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Mentor(models.Model):

    # already applied for this semester
    applied = models.BooleanField(default = False)

    # name data of applicants
    RIN = models.CharField(max_length=9)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    GPA = models.IntegerField()
    RPI_email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50) # ???
    recommender = models.CharField(max_length=50)

    step = models.IntegerField(default = 1)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE)
    #open = models.IntegerField(default=0)
    def __str__(self):
        return ""

class Course(models.Model):
    class_title = models.CharField(max_length=4)
    class_number = models.IntegerField


class Professor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)

