import datetime
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from .prefpy.mechanism import *
from groups.models import *
from django.conf import settings

def switchSubject(x, title, creator):
    return {
        'invite': 'You have been invited to vote on ' + title,
        'remove': 'You have been removed from ' + title,
        'start': title + ' has started!',
        'stop': title + ' has stopped',
    }.get(x, "A message from " + creator)

def switchEmail(x, name, creator, request, question_id):
    return {
        'invite': 'Hello ' + name + ',\n\n' + creator
                + ' has invited you to vote on a poll. Please visit '
                + request.build_absolute_uri(reverse('polls:detail', args=[question_id]))
                + ' to vote.\n\nSincerely,\nOPRAH Staff',
        'remove': 'Hello ' + name + ',\n\n' + creator
                + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff',
        'start': 'Hello ' + name + ',\n\n' + creator
                + ' has started a poll. It is now available to vote on at '
                + request.build_absolute_uri(reverse('polls:detail', args=[question_id]))
                + ' to vote.\n\nSincerely,\nOPRAH Staff',
        'stop': 'Hello ' + name + ',\n\n' + creator
                + ' has ended a poll. Please visit '
                + request.build_absolute_uri(reverse('polls:index'))
                + ' to view the decision.\n\nSincerely,\nOPRAH Staff',
    }.get(x, x)

#function to send email
def sendEmail(request, question_id, type):
    question = get_object_or_404(Question, pk=question_id)
    title = question.question_text
    creator_obj = User.objects.get(id=question.question_owner_id)
    creator = creator_obj.username
    if creator_obj.first_name != "":
        creator = creator_obj.first_name + " " + creator_obj.last_name

    if type == 'invite' or type == 'remove':
        voters = request.POST.getlist('voters')
    else:
        voters = question.question_voters.all()
    for voter in voters:
        if type == 'invite' or type == 'remove':
     	    voter = get_object_or_404(User, username=voter)
        name = voter.username
        if voter.first_name != "":
            name = voter.first_name + " " + voter.last_name
        mail.send_mail(switchSubject(type, title, creator),
            switchEmail(type, name, creator, request, question_id),
            'oprahprogramtest@gmail.com',[voter.email])
