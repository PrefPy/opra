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


        
# https://djangosnippets.org/snippets/2451/
# unmodified version of Dict
class Dict(models.Model):
    """A model that represents a Dict. This model implements most of the Dict interface,
    allowing it to be used like a python Dict.

    """
    name = models.CharField(max_length = 1000)

    @staticmethod
    def getDict(name):
        """Get the Dict of the given name.

        """
        df = Dict.objects.select_related().get(name=name)

        return df

    def __getitem__(self, key):
        """Returns the value of the selected key.

        """
        return self.keyvaluepair_set.get(key=key).value

    def __setitem__(self, key, value):
        """Sets the value of the given key in the Dict.

        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)

        except KeyValuePair.DoesNotExist:
            KeyValuePair.objects.create(container=self, key=key, value=value)

        else:
            kvp.value = value
            kvp.save()

    def __delitem__(self, key):
        """Removed the given key from the Dict.

        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)

        except KeyValuePair.DoesNotExist:
            raise KeyError

        else:
            kvp.delete()

    def __len__(self):
        """Returns the length of this Dict.

        """
        return self.keyvaluepair_set.count()

    def iterkeys(self):
        """Returns an iterator for the keys of this Dict.

        """
        return iter(kvp.key for kvp in self.keyvaluepair_set.all())

    def itervalues(self):
        """Returns an iterator for the keys of this Dict.

        """
        return iter(kvp.value for kvp in self.keyvaluepair_set.all())

    __iter__ = iterkeys

    def iteritems(self):
        """Returns an iterator over the tuples of this Dict.

        """
        return iter((kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all())

    def keys(self):
        """Returns all keys in this Dict as a list.

        """
        return [kvp.key for kvp in self.keyvaluepair_set.all()]

    def values(self):
        """Returns all values in this Dict as a list.

        """
        return [kvp.value for kvp in self.keyvaluepair_set.all()]

    def items(self):
        """Get a list of tuples of key, value for the items in this Dict.
        This is modeled after dict.items().

        """
        return [(kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all()]

    def get(self, key, default=None):
        """Gets the given key from the Dict. If the key does not exist, it
        returns default.

        """
        try:
            return self[key]

        except KeyError:
            return default

    def has_key(self, key):
        """Returns true if the Dict has the given key, false if not.

        """
        return self.contains(key)

    def contains(self, key):
        """Returns true if the Dict has the given key, false if not.

        """
        try:
            self.keyvaluepair_set.get(key=key)
            return True

        except KeyValuePair.DoesNotExist:
            return False

    def clear(self):
        """Deletes all keys in the Dict.

        """
        self.keyvaluepair_set.all().delete()

    def __unicode__(self):
        """Returns a unicode representation of the Dict.

        """
        return unicode(self.asPyDict())

    def asPyDict(self):
        """Get a python Dict that represents this Dict object.
        This object is read-only.

        """
        fieldDict = dict()

        for kvp in self.keyvaluepair_set.all():
            fieldDict[kvp.key] = kvp.value

        return fieldDict


class KeyValuePair(models.Model):
    """A Key-Value pair with a pointer to the Dict that owns it.

    """
    container = models.ForeignKey(Dict, db_index=True, on_delete = models.CASCADE)
    key = models.CharField(max_length=240, db_index=True)
    value = models.CharField(max_length=240, db_index=True)

# The model for a course
class Course(models.Model):
    subject = models.CharField(max_length=4)  # e.g CSCI              
    number = models.CharField(max_length=4, default="1000") # e.g 1100
    name = models.CharField(max_length=50, default = 'none') # e.g Intro to programming

    # This should change to foreignkey afterwards
    # But we left this now to make the implementation easy
    instructor = models.CharField(max_length=50, default = 'none') # Instrcutor's name

    # feature weights to represent the pref
    feature_cumlative_GPA = models.IntegerField(default=0)
    feature_has_taken = models.IntegerField(default=0)
    feature_course_GPA = models.IntegerField(default=0)
    feature_mentor_exp = models.IntegerField(default=0)

    
    def __str__(self):
        return self.subject + " " + self.number + " " + self.name

# the model to represent a mentor applicant
class Mentor(models.Model):

    # already applied for this semester
    applied = models.BooleanField(default = False)
    #step = models.IntegerField(default = 1)

    # Personal Info & preference of applicants
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
    compensation = models.CharField(max_length=1, choices = compensation_choice, default='1')

    # Course preference of applicants, the data model here is dictionary
    # Yeah we can do charfield... will change it afterwards
    course_pref = models.ForeignKey(Dict, on_delete = models.CASCADE, default = None)
   
    # Many to one relation 
    # mentor_course -> {s1, s2, s3, ...}
    # To get all the mentors in a course: course.mentor_set.all()
    mentored_course = models.ForeignKey(Course, on_delete = models.CASCADE, default = None, null=True)


    def __str__(self):
        return self.first_name + " " + self.last_name



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
    


class Instrcutor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + " " + self.last_name