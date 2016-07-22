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

def setupEmail(question):
    title = question.question_text
    creator = question.question_owner.username
    emailInvite = Email(question=question, type=1,
        subject="You have been invited to vote on " + title,
        message='Hello [user_name],\n\n' + creator
                + ' has invited you to vote on a poll. Please login at [url] to check it out.\n\nSincerely,\nOPRAH Staff')
    emailRemove = Email(question=question, type=2,
        subject="You have been removed from " + title,
        message='Hello [user_name],\n\n' + creator
                + ' has deleted you from a poll.\n\nSincerely,\nOPRAH Staff')
    emailStart = Email(question=question, type=3,
        subject=title + ' has started!',
        message='Hello [user_name],\n\n' + creator
                + ' has started a poll. It is now available to vote on at [url] \n\nSincerely,\nOPRAH Staff')
    emailStop = Email(question=question, type=4,
        subject=title + ' has stopped',
        message='Hello [user_name],\n\n' + creator
                + ' has ended a poll. Please visit [url] to view the decision.\n\nSincerely,\nOPRAH Staff')
    emailInvite.save()
    emailRemove.save()
    emailStart.save()
    emailStop.save()

def getOptions(items):
    arr = []
    for item in items:
        arr.append(item.item_text)
    return arr

def switchModel(type, question, request):
    if type == 'invite':
        email = Email.objects.filter(question=question, type=1)
    if type == 'remove':
        email = Email.objects.filter(question=question, type=2)
    if type == 'start':
        email = Email.objects.filter(question=question, type=3)
    if type == 'stop':
        email = Email.objects.filter(question=question, type=4)
    if type == 'now':
        return [request.POST.get('subject'), request.POST.get('message')]
    if len(email) != 1:
        setupEmail(question)
    return [email[0].subject, email[0].message]

def translateEmail(text, uname, url):
    text = text.replace("[user_name]", uname)
    text = text.replace("[url]", url)
    return text

def translateHTML(text, uname, url, options):
    text = translateEmail(text, uname, url)
    text = "<p>" + text + "</p>"
    text = text.replace("\n\n", "</p><br /><p>")
    text = text.replace("\n", "</p><p>")
    text += options
    return text

#function to send email
def sendEmail(request, question_id, type):
    question = get_object_or_404(Question, pk=question_id)
    email = switchModel(type, question, request)
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
            options = ''
            for i in items:
                rand = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
                response = EmailResponse(item=i, user=voter, identity=rand)
                response.save()
                options += '<p><a href=\'' + request.build_absolute_uri(reverse('polls:index') + str(response.pk) + "/" + rand + "/voteEmail/") + '\'>' + i.item_text + '</a></p>'
        if voter.first_name != "":
            name = voter.first_name + " " + voter.last_name
        url = request.build_absolute_uri(reverse('appauth:login')+'?name='+uname)
        mail.send_mail(translateEmail(email[0], name, url),
            translateEmail(email[1], name, url),
            'oprahprogramtest@gmail.com',[voter.email],
            html_message=translateHTML(email[1], name, url, options))

#function to send email
def emailNow(request, question_id):
    sendEmail(request, question_id, "now")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#function to send email
def emailOptions(request, question_id):
    sendEmail(request, question_id, "start")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def emailSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    emailInvite = Email.objects.filter(question=question, type=1)[0]
    emailInvite.subject = request.POST.get('inviteSubject')
    emailInvite.message = request.POST.get('inviteMessage')
    emailInvite.save()
    emailDelete = Email.objects.filter(question=question, type=2)[0]
    emailDelete.subject = request.POST.get('deleteSubject')
    emailDelete.message = request.POST.get('deleteMessage')
    emailDelete.save()
    emailStart = Email.objects.filter(question=question, type=3)[0]
    emailStart.subject = request.POST.get('startSubject')
    emailStart.message = request.POST.get('startMessage')
    emailStart.save()
    emailStop = Email.objects.filter(question=question, type=4)[0]
    emailStop.subject = request.POST.get('stopSubject')
    emailStop.message = request.POST.get('stopMessage')
    emailStop.save()
    question.emailInvite = request.POST.get('emailInvite') == 'email'
    question.emailDelete = request.POST.get('emailDelete') == 'email'
    question.emailStart = request.POST.get('emailStart') == 'email'
    question.emailStop = request.POST.get('emailStop') == 'email'
    question.save()
    request.session['setting'] = 5
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