from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail

class addGroupView(generic.ListView):
    template_name = 'groups/addgroup.html'
    def get_context_data(self, **kwargs):
        ctx = super(addGroupView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        return ctx
    
    def get_queryset(self):
        return Group.objects.order_by('-pub_date')  

def addgroup(request):
    context = RequestContext(request)
    if request.method == 'POST':
        groupName = request.POST['groupName']
        group = Group(name = groupName, owner = request.user)
        group.save()
        newMembers = request.POST.getlist('voters')
        for member in newMembers:
            memberObj = User.objects.get(username=member)
            group.members.add(memberObj.id)
        return HttpResponseRedirect('/groups/%s/members' % group.id)
    return render_to_response('groups/addgroup.html', {}, context)

def addmember(request, group_id):
    context = RequestContext(request)
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        newMembers = request.POST.getlist('members')
        for member in newMembers:
            memberObj = User.objects.get(username=member)
            group.members.add(memberObj.id)
        return HttpResponseRedirect('/groups/%s/members' % group.id)
    return render_to_response('members.html', {}, context)  

class MembersView(generic.DetailView):
    model = Group
    template_name = 'groups/members.html'
    def get_context_data(self, **kwargs):
        ctx = super(MembersView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        return ctx

def addgroupvoters(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    creator_obj = User.objects.get(id=question.question_owner_id)
    title = question.question_text
    creator = creator_obj.username
    newGroups = request.POST.getlist('groups')
    for group in newGroups:
        groupObj = Group.objects.get(name=group)
        for voter in groupObj.members.all():
            if voter not in question.question_voters.all():
                voterObj = User.objects.get(username=voter)
                question.question_voters.add(voterObj.id)
                mail.send_mail('You have been invited to vote on ' + title,
                    'Hello ' + voterObj.username + ',\n\n' + creator
                    + ' has invited you to vote on a poll. Please visit http://localhost:8000/polls/'
                    + question_id + ' to vote.\n\nSincerely,\nOPRAH Staff',
                    'oprahprogramtest@gmail.com',[voterObj.email])
    return HttpResponseRedirect('/polls/%s/settings' % question_id)