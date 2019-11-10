from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


@python_2_unicode_compatible

# a helper function to ensure min and max value
class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value' : self.max_value}
        defaults.update(kwargs)
        return super(MinMaxFloat, self).formfield(**defaults)

# the model for a mentor applicant
class Mentor(models.Model):

    # already applied for this semester
    applied = models.BooleanField(default = False)
    #step = models.IntegerField(default = 1)

    # Personal Info of applicants
    RIN = models.CharField(max_length=9, validators=[MinLengthValidator(9)], primary_key=True)
    first_name = models.CharField(max_length=50) # first name
    last_name = models.CharField(max_length=50) # last name

    GPA = MinMaxFloat(min_value = 0.0, max_value = 4.0)

    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50) # ???
    recommender = models.CharField(max_length=50)

    # Compensation Choices
    compensation_choice = (
                     ('1', 'Pay'),
                     ('2', 'Credit'),
                     ('3', 'No Preference'),
                     )
    compensation = models.CharField(max_length=1, choices=compensation_choice, default='1')

   
    def __str__(self):
        return ""

# The model for a course
class Course(models.Model):
    subject = models.CharField(max_length=4)  # e.g CSCI              
    number = models.CharField(max_length=4, default="1000") # e.g 1100
    name = models.CharField(max_length=50, default = 'none') # e.g Intro to programming
    instructor = models.CharField(max_length=50, default = 'none') # Instrcutor's name

    feature_cumlative_GPA = models.IntegerField(default=0)
    feature_has_taken = models.IntegerField(default=0)
    feature_course_GPA = models.IntegerField(default=0)
    feature_mentor_exp = models.IntegerField(default=0)


class Grade(models.Model):
    student = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    grades = (
            ('a', 'A'),
            ('a-', 'A-'),
            ('b+', 'B+'),
            ('b', 'B'),
            ('b-', 'B-'),
            ('c+', 'C+'),
            ('c', 'C'),
            ('c-', 'C-'),
            ('d+', 'D+'),
            ('d', 'D'),
            ('f', 'F'),
            ('p', 'Progressing'),
            ('n', 'Not Taken'),
            )
    
    student_grade = models.CharField(max_length=1, choices = grades, default='n') # The student's grade of this course
    have_taken = models.BooleanField(default = False) # Whether this studnet have taken this course
    mentor_exp = models.BooleanField(default = False) # Whether this studnet have mentored this course
    


class Professor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)

