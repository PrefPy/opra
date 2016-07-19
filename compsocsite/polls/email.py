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
import random
import string

def switchSubject(x, title, creator):
    return {
        'invite': 'You have been invited to vote on ' + title,
        'remove': 'You have been removed from ' + title,
        'start': title + ' has started!',
        'stop': title + ' has stopped',
    }.get(x, "A message from " + creator)

def switchEmail(x, name, uname, creator, request, question_id):
    return {
        'invite': 'Hello ' + name + ',\n\n' + creator
                + ' has invited you to vote on a poll. Please login at '
                + request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
                + ' to check out.\n\nSincerely,\nOPRAH Staff',
        'remove': 'Hello ' + name + ',\n\n' + creator
                + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff',
        'start': 'Hello ' + name + ',\n\n' + creator
                + ' has started a poll. It is now available to vote on at '
                + request.build_absolute_uri(reverse('polls:detail', args=[question_id]))
                + ' \n\nSincerely,\nOPRAH Staff',
        'stop': 'Hello ' + name + ',\n\n' + creator
                + ' has ended a poll. Please visit '
                + request.build_absolute_uri(reverse('polls:index'))
                + ' to view the decision.\n\nSincerely,\nOPRAH Staff',
    }.get(x, x)

def switchHTML(x, name, uname, creator, request, question_id, options):
    return {
        'invite': '<h1>Hello ' + name + ',</h1><p>' + creator
                + ' has invited you to vote on a poll. Please login <a href=\''
                + request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
                + '\'>here</a> to check it out.</p><p>Sincerely,</p><p>OPRAH Staff</p>',
        'remove': 'Hello ' + name + ',\n\n' + creator
                + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff',
        'start': '<h1>Hello ' + name + ',</h1><p>' + creator
                + ' has started a poll. It is now available to vote on <a href=\''
                + request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
                + '\'>here</a>.</p>' + options + '<p>Sincerely,</p><p>OPRAH Staff</p>',
        'stop': 'Hello ' + name + ',\n\n' + creator
                + ' has ended a poll. Please visit '
                + request.build_absolute_uri(reverse('polls:index'))
                + ' to view the decision.\n\nSincerely,\nOPRAH Staff',
    }.get(x, x)

def getOptions(items):
    arr = []
    for item in items:
        arr.append(item.item_text)
    return arr

#function to send email
def sendEmail(request, question_id, type):
    question = get_object_or_404(Question, pk=question_id)
    options = ''
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
        uname = voter.username
        if question.poll_algorithm == 1 and type == 'start':
            items = Item.objects.all().filter(question=question)
            item_array = getOptions(items)
            for i in items:
                rand = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
                response = EmailResponse(item=i, user=voter, identity=rand)
                response.save()
                options += '<p><a href=\'' + request.build_absolute_uri(reverse('polls:index') + str(response.pk) + "/" + rand + "/voteEmail/") + '\'>' + i.item_text + '</a></p>'
        if voter.first_name != "":
            name = voter.first_name + " " + voter.last_name
        mail.send_mail(switchSubject(type, title, creator),
            switchEmail(type, name, uname, creator, request, question_id),
            'oprahprogramtest@gmail.com',[voter.email],
            html_message=switchHTML(type, name, uname, creator, request, question_id, options))

def emailSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.emailInvite = request.POST.get('emailInvite') == 'email'
    question.emailDelete = request.POST.get('emailDelete') == 'email'
    question.emailStart = request.POST.get('emailStart') == 'email'
    question.emailStop = request.POST.get('emailStop') == 'email'
    question.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def voteEmail(request, key, resp_id):
    eResp = get_object_or_404(EmailResponse, pk=resp_id, identity=key)
    question = eResp.item.question
    if question.status == 2:
        arr = question.item_set.all().exclude(pk=eResp.item.pk)
        prefOrder = ["item" + eResp.item.item_text]
        for a in arr:
            prefOrder.append("item" + a.item_text)
        
        # make Response object to store data
        response = Response(question=question, user=eResp.user, timestamp=timezone.now())
        response.save()
        d = response.dictionary_set.create(name = eResp.user.username + " Preferences")

        # find ranking student gave for each item under the question
        item_num = 1
        for item in question.item_set.all():
            arrayIndex = prefOrder.index("item" + str(item))
            
            if arrayIndex == -1:
                # set value to lowest possible rank
                d[item] = question.item_set.all().count()
            else:
                # add 1 to array index, since rank starts at 1
                rank = (prefOrder.index("item" + str(item))) + 1
                # add pref to response dict
                d[item] = rank
            d.save()
            item_num += 1

        #get current winner
        old_winner = OldWinner(question=question, response=response)
        old_winner.save()

        return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))