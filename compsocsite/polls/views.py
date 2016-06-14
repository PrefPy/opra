import datetime

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

# view for homepage - index of questions & results
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
    	return Question.objects.all().order_by('-pub_date')

def addView(request):
    context = RequestContext(request)
    if request.method == 'POST':
        questionString = request.POST['questionTitle']
        question = Question(question_text=questionString, pub_date=timezone.now(), question_owner=request.user)
        question.save()
        item1 = Item(question=question, item_text=request.POST['choice1'])
        item2 = Item(question=question, item_text=request.POST['choice2'])
        item3 = Item(question=question, item_text=request.POST['choice3'])
        item1.save()
        item2.save()
        item3.save()
        return HttpResponseRedirect('/polls/%s/settings' % question.id)
    return render_to_response('polls/add.html', {}, context)    

def editAction(request, question_id):
    context = RequestContext(request)
    
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=question_id)
        item_text = request.POST['choice']
        item = Item(question=question, item_text = item_text)
        item.save()
        return HttpResponse("Your question: " + question.question_text+" has been  successfully edited")
    return render_to_response('polls/action.html', {"qid":question_id}, context)

class EditView(generic.ListView):
    template_name = 'polls/edit.html'
    context_object_name = 'question_listasd'
    
    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')

class addGroupView(generic.ListView):
    template_name = 'polls/addgroup.html'
    def get_context_data(self, **kwargs):
        ctx = super(addGroupView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        return ctx
    def get_queryset(self):
    	return Question.objects.all().order_by('-pub_date')

class MembersView(generic.DetailView):
    model = Group
    template_name = 'polls/members.html'
    def get_context_data(self, **kwargs):
        ctx = super(MembersView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        return ctx
# view for question detail
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# view for settings detail
class SettingsView(generic.DetailView):
    model = Question
    template_name = 'polls/settings.html'
    def get_context_data(self, **kwargs):
        ctx = super(SettingsView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# view for results detail
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# view for submission confirmation
class ConfirmationView(generic.DetailView):
    model = Question
    template_name = 'polls/confirmation.html'
    
class PreferenceView(generic.DetailView):
    model = Question
    template_name = 'polls/preferences.html'
    def get_context_data(self, **kwargs):
        ctx = super(PreferenceView, self).get_context_data(**kwargs)
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        ctx['mostRecentResponse'] = currentUserResponses[0] if (len(currentUserResponses) > 0) else None
        ctx['history'] = currentUserResponses[1:]
        
        all_responses = self.object.response_set.reverse()
        latest_responses = []
        if len(all_responses) > 0:
            latest_responses.append(all_responses[0])   
        previous_responses = []
        others = all_responses[1:]
        
        for response1 in others:
            if response1.user == None:
                continue
	    
            add = True
            for response2 in latest_responses:
                if response1.user.username == response2.user.username:
                    add = False
                    previous_responses.append(response1)
                    break

            if add:
                latest_responses.append(response1)   
        
        ctx['latest_responses'] = latest_responses
        ctx['previous_responses'] = previous_responses
        return ctx

#function to add voter to voter list (invite only)
def addvoter(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    newVoters = request.POST.getlist('voters')
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.add(voterObj.id)
        mail.send_mail('You have been invited to vote!',
            'Hello,\n\nYou have been invited to vote on a poll.\n\nSincerely,\nOPRAH Staff',
            'oprahprogramtest@gmail.com',[voterObj.email])
    return HttpResponseRedirect('/polls/%s/settings' % question_id)

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
        return HttpResponse("Your group: " + groupName)
    return render_to_response('polls/addgroup.html', {}, context)

def addmember(request, group_id):
    context = RequestContext(request)
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        newMembers = request.POST.getlist('members')
        for member in newMembers:
            memberObj = User.objects.get(username=member)
            group.members.add(memberObj.id)
        return HttpResponse("New members added.")
    return render_to_response('polls/members.html', {}, context)  
# function to process student submission
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # make Response object to store data
    response = Response(question=question, user=request.user, timestamp=timezone.now())
    response.save()
    d = response.dictionary_set.create(name = response.user.username + " Preferences")

    # find ranking student gave for each item under the question
    item_num = 1
    for item in question.item_set.all():
        try:
            selected_choice = request.POST["item" + str(item_num)]
        except:
            # set value to lowest possible rank
            d[item] = question.item_set.all().count()
        else:
            # add pref to response dict
            d[item] = int(selected_choice)
        d.save()
        item_num += 1
    return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))


