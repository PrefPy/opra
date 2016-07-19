from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import os
from django.conf import settings

# Models

# question that will receive responses
@python_2_unicode_compatible
class Question(models.Model):
    question_text = models.CharField(max_length=20)
    question_desc = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='static/img/items/', blank=True, null=True)
    imageURL = models.CharField(max_length=500, blank=True, null=True)
    pub_date = models.DateTimeField('date published')
    follow_up = models.OneToOneField('Question', on_delete=models.CASCADE, null = True, blank = True)
    question_owner = models.ForeignKey(User, null=True)
    question_voters = models.ManyToManyField(User, related_name='poll_participated')
    status = models.IntegerField(default=1)
    display_pref = models.IntegerField(default=1)
    emailInvite = models.BooleanField(default=True)
    emailDelete = models.BooleanField(default=True)
    emailStart = models.BooleanField(default=True)
    emailStop = models.BooleanField(default=True)
    poll_algorithm = models.IntegerField(default=1)
    question_type = models.IntegerField(default=1)
    winner = models.CharField(max_length=200)
    m_poll = models.BooleanField(default=False)
    open = models.BooleanField(default=False)
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    def get_voters(self):
        return ",".join([str(voter) for voter in self.question_voters.all()])

#Helper function for image
def get_image_path(instance, filename):
    return 'static/img/items/'

# item to rank in a question
@python_2_unicode_compatible
class Item(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    item_text = models.CharField(max_length=200)
    image = models.ImageField(upload_to='static/img/items/', blank=True, null=True)
    imageURL = models.CharField(max_length=500, blank=True, null=True)
    def __str__(self):
        return self.item_text

# voter without an user account
@python_2_unicode_compatible
class AnonymousVoter(models.Model):
    name = models.CharField(max_length=50)
    question = models.ForeignKey(Question)
    def __str__(self):
        return self.name    

# all information pertaining to a response that a student made to a question
@python_2_unicode_compatible
class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, null = True, blank = True)
    timestamp = models.DateTimeField('response timestamp')
    allocation = models.ForeignKey(Item, default=None, null = True, blank = True, on_delete=models.CASCADE) # assigned by algorithm function
    anonymous_voter = models.ForeignKey(AnonymousVoter, null=True, blank = True)
    comment = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return "Response of user " + self.user.username + "\nfor question " + self.question.question_text
    class Meta:
        ordering = ['timestamp']

# all information pertaining to a response that a student made to a question
@python_2_unicode_compatible
class EmailResponse(models.Model):
    identity = models.CharField(max_length=20, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, null=True)
    def __str__(self):
        return ""     

# a winner at a certain point in time
@python_2_unicode_compatible
class OldWinner(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    def __str__(self):
        return (str(self.response.timestamp.time()))

# a single voter in the allocation
@python_2_unicode_compatible
class AllocationVoter(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return "User " + self.user.username + " assigned to " + self.question.question_text 
    
# a poll can have multiple dependent polls (must be part of the same multipoll)
class Combination(models.Model):
    target_question = models.ForeignKey(Question)
    dependent_questions = models.ManyToManyField(Question, related_name="dependent_questions")
    user = models.ForeignKey(User)
    dependencies = models.ManyToManyField(Item)
    response = models.OneToOneField(Response,null=True, blank=True)

# link the choices for the dependent polls to a response
class ConditionalItem(models.Model):
    combination = models.ForeignKey(Combination)
    items = models.ManyToManyField(Item)
    response = models.OneToOneField(Response, null=True, blank=True)

# Dictionary Helper Models - from https://djangosnippets.org/snippets/2451/
# Models include modifications to be used specifically for holding student preferences - these changes are marked with comments

# collection of a student's preferences within a single response (to a single question)
class Dictionary(models.Model):
    """A model that represents a dictionary. This model implements most of the dictionary interface,
    allowing it to be used like a python dictionary.
    """
    name = models.CharField(max_length=255)
    response = models.ForeignKey(Response, default=None, on_delete=models.CASCADE) # added to original model
    @staticmethod
    def getDict(name):
        """Get the Dictionary of the given name.
        """
        df = Dictionary.objects.select_related().get(name=name)
        return df

    def __getitem__(self, key):
        """Returns the value of the selected key.
        """
        return self.keyvaluepair_set.get(key=key).value

    def __setitem__(self, key, value):
        """Sets the value of the given key in the Dictionary.
        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)
        except KeyValuePair.DoesNotExist:
            KeyValuePair.objects.create(container=self, key=key, value=value)
        else:
            kvp.value = value
            kvp.save()

    def __delitem__(self, key):
        """Removed the given key from the Dictionary.
        """
        try:
            kvp = self.keyvaluepair_set.get(key=key)
        except KeyValuePair.DoesNotExist:
            raise KeyError
        else:
            kvp.delete()

    def __len__(self):
        """Returns the length of this Dictionary.
        """
        return self.keyvaluepair_set.count()

    def iterkeys(self):
        """Returns an iterator for the keys of this Dictionary.
        """
        return iter(kvp.key for kvp in self.keyvaluepair_set.all())

    def itervalues(self):
        """Returns an iterator for the values of this Dictionary.
        """
        return iter(kvp.value for kvp in self.keyvaluepair_set.all())

    __iter__ = iterkeys

    def iteritems(self):
        """Returns an iterator over the tuples of this Dictionary.
        """
        return iter((kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all())

    def keys(self):
        """Returns all keys in this Dictionary as a list.
        """
        return [kvp.key for kvp in self.keyvaluepair_set.all()]

    def values(self):
        """Returns all values in this Dictionary as a list.
        """
        return [kvp.value for kvp in self.keyvaluepair_set.all()]

    def sorted_values(self):
        """Sorts the Dictionary by value"""
        return list(sorted(self.items(), key=lambda kv: (kv[1], kv[0])))

    def items(self):
        """Get a list of tuples of key, value for the items in this Dictionary.
        This is modeled after dict.items().
        """
        return [(kvp.key, kvp.value) for kvp in self.keyvaluepair_set.all()]

    def get(self, key, default=None):
        """Gets the given key from the Dictionary. If the key does not exist, it
        returns default.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def has_key(self, key):
        """Returns true if the Dictionary has the given key, false if not.
        """
        return self.contains(key)

    def contains(self, key):
        """Returns true if the Dictionary has the given key, false if not.
        """
        try:
            self.keyvaluepair_set.get(key=key)
            return True
        except KeyValuePair.DoesNotExist:
            return False

    def clear(self):
        """Deletes all keys in the Dictionary.
        """
        self.keyvaluepair_set.all().delete()

    def __unicode__(self):
        """Returns a unicode representation of the Dictionary.
        """
        return unicode(self.asPyDict())

    def asPyDict(self):
        """Get a python dictionary that represents this Dictionary object.
        This object is read-only.
        """
        fieldDict = dict()
        for kvp in self.keyvaluepair_set.all():
            fieldDict[kvp.key] = kvp.value
        return fieldDict

# key-value pair of an item and the ranking a student gave it in their response
class KeyValuePair(models.Model):
    """A Key-Value pair with a pointer to the Dictionary that owns it.
    """
    container = models.ForeignKey(Dictionary, db_index=True)
    key = models.ForeignKey(Item, default=None, on_delete=models.CASCADE, db_index=True) # changed from original model
    value = models.IntegerField(default=0, db_index=True) # changed from original model
