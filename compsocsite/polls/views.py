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
from .prefpy.mechanism import *

# view for homepage - index of questions & results
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'
    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx['groups'] = Group.objects.all()
        return ctx
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

def addChoice(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    item_text = request.POST['choice']
    item = Item(question=question, item_text=item_text)
    item.save()
    return HttpResponseRedirect('/polls/%s/settings' % question.id)

def deleteChoice(request, choice_id):
    item = Item.objects.filter(id=choice_id)
    question = item[0].question
    item.delete()
    return HttpResponseRedirect('/polls/%s/settings' % question.id)

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
    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        if len(currentUserResponses) > 0:
            mostRecentResponse = currentUserResponses[0]
            selectionArray = []             
            for d in mostRecentResponse.dictionary_set.all():               
                selectionArray = d.values()
            ctx['currentSelection'] = selectionArray
        return ctx
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
        ctx['groups'] = Group.objects.all()
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

# view that displays votes
class PreferenceView(generic.DetailView):
    model = Question
    template_name = 'polls/preferences.html'
    def get_context_data(self, **kwargs):
        ctx = super(PreferenceView, self).get_context_data(**kwargs)
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        ctx['mostRecentResponse'] = currentUserResponses[0] if (len(currentUserResponses) > 0) else None
        ctx['history'] = currentUserResponses[1:]
        
        all_responses = self.object.response_set.reverse()
        (latest_responses, previous_responses) = categorizeResponses(all_responses)
        ctx['latest_responses'] = latest_responses
        ctx['previous_responses'] = previous_responses    
        return ctx

#separate the user votes into two categories: (1)most recent (2)previous history
def categorizeResponses(all_responses):
    latest_responses = []
    previous_responses = []
    
    if len(all_responses) > 0:
        #the first response must be the most recent 
        latest_responses.append(all_responses[0])   
    
    others = all_responses[1:]
    
    #the outer loop goes through all the responses
    for response1 in others:
        if response1.user == None:
            continue
        
        add = True
        #check if the user has voted multiple times
        for response2 in latest_responses:
            if response1.user.username == response2.user.username:
                add = False
                previous_responses.append(response1)
                break

        #this is the most recent vote
        if add:
            latest_responses.append(response1)   
    
    return (latest_responses, previous_responses)

# view that displays vote results using various algorithms
class VoteResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/vote_rule.html'
    def get_context_data(self, **kwargs):
        ctx = super(VoteResultsView, self).get_context_data(**kwargs)
        
        all_responses = self.object.response_set.reverse()
        (latest_responses, previous_responses) = categorizeResponses(all_responses)
        ctx['latest_responses'] = latest_responses
        ctx['previous_responses'] = previous_responses
        ctx['cand_map'] = getCandidateMap(latest_responses[0]) if (len(latest_responses) > 0) else None
        ctx['vote_results'] = getVoteResults(latest_responses)        
        return ctx

#get a list of options for this poll
def getCandidateMap(response):
    responseValues = response.dictionary_set.all()
    candMap = {}
    for d in responseValues:
        counter = 0
        for item in d.items():
            candMap[counter] = item[0]
            counter += 1
    return candMap

#convert a user's preference into a 2d map
def getPreferenceGraph(response):
    prefGraph = {}
    responseValues = response.dictionary_set.all()
    candMap = getCandidateMap(response)

    for cand1Index in candMap:
        tempDict = {}
        for cand2Index in candMap:
            if cand1Index == cand2Index:
                continue
            
            cand1 = candMap[cand1Index]
            cand2 = candMap[cand2Index]
            cand1Rank = response.dictionary_set.all()[0].get(cand1)
            cand2Rank = response.dictionary_set.all()[0].get(cand2)
            #lower number is better (i.e. rank 1 is better than rank 2)
            if cand1Rank < cand2Rank:
                tempDict[cand2Index] = 1
            elif cand2Rank < cand1Rank:
                tempDict[cand2Index] = -1
            else:
                tempDict[cand2Index] = 0
        prefGraph[cand1Index] = tempDict
    
    return prefGraph

#initialize a profile object using all the preferences
def getPollProfile(latest_responses):
    if len(latest_responses) == 0:
        return None
    
    prefList = []
    for response in latest_responses:
        prefGraph = getPreferenceGraph(response)
        userPref = Preference(prefGraph)
        prefList.append(userPref)
    return Profile(getCandidateMap(latest_responses[0]), prefList)

#calculate the results of the vote using different algorithms
def getVoteResults(latest_responses):
    pollProfile = getPollProfile(latest_responses)
    if pollProfile == None:
        return []

    #make sure no ties or incomplete results are in the votes
    if pollProfile.getElecType() != "soc":
        return []

    scoreVectorList = []
    scoreVectorList.append(MechanismBorda().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismPlurality().getCandScoresMap(pollProfile))  
    scoreVectorList.append(MechanismVeto().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismKApproval(3).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismSimplifiedBucklin().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismCopeland(1).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismMaximin().getCandScoresMap(pollProfile))
    return scoreVectorList

#function to add voter to voter list (invite only)
def addvoter(request, question_id):
    question    = get_object_or_404(Question, pk=question_id)
    creator_obj = User.objects.get(id=question.question_owner_id)

    newVoters = request.POST.getlist('voters')
    title = question.question_text
    creator = creator_obj.username
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.add(voterObj.id)
        mail.send_mail('You have been invited to vote on ' + title,
            'Hello ' + voterObj.username + ',\n\n' + creator
            + ' has invited you to vote on a poll. Please visit http://localhost:8000/polls/'
            + question_id + ' to vote.\n\nSincerely,\nOPRAH Staff',
            'oprahprogramtest@gmail.com',[voterObj.email])
    return HttpResponseRedirect('/polls/%s/settings' % question_id)

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

#function to send email
def sendEmail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    creator_obj = User.objects.get(id=question.question_owner_id)
    title = question.question_text
    creator = creator_obj.username
    voters = question.question_voters.all()
    for voter in voters:
        mail.send_mail('Reminder to vote on ' + title,
            request.POST.get('email_txt'),
            'oprahprogramtest@gmail.com',[voter.email])
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
        return HttpResponseRedirect('/polls/%s/members' % group.id)
    return render_to_response('polls/addgroup.html', {}, context)

def addmember(request, group_id):
    context = RequestContext(request)
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        newMembers = request.POST.getlist('members')
        for member in newMembers:
            memberObj = User.objects.get(username=member)
            group.members.add(memberObj.id)
        return HttpResponseRedirect('/polls/%s/members' % group.id)
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