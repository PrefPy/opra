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
from .email import sendEmail
from groups.models import *
from django.conf import settings
from multipolls.models import *
from .algorithms import *

# view for homepage - index of questions & results
class IndexView(generic.ListView):
    template_name = 'polls/index2.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')
    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx['multipolls'] = MultiPoll.objects.all()
        return ctx

class MainView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')
    
    
#the first step of creating new vote
def AddStep1View(request):
    context = RequestContext(request)
    if request.method == 'POST':
        questionString = request.POST['questionTitle']   
        questionDesc = request.POST['desc']
        questionType = request.POST['questiontype']
        imageURL = request.POST['imageURL']
        # create a new question using information from the form and inherit settings from the user's preferences
        question = Question(question_text=questionString, question_desc=questionDesc,
            pub_date=timezone.now(), question_owner=request.user,
            display_pref=request.user.userprofile.displayPref, emailInvite=request.user.userprofile.emailInvite,
            emailDelete=request.user.userprofile.emailDelete, emailStart=request.user.userprofile.emailStart,
            emailStop=request.user.userprofile.emailStop)
        if request.FILES.get('docfile') != None:
            question.image = request.FILES.get('docfile')
        elif imageURL != '':
            question.imageURL = imageURL 
        question.question_type = questionType
        question.save()
        return HttpResponseRedirect(reverse('polls:AddStep2', args=(question.id,)))
    return render_to_response('polls/add_step1.html', {}, context)

class AddStep2View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step2.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep2View, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class AddStep3View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step3.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep3View, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
class AddStep4View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step4.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep4View, self).get_context_data(**kwargs)
        ctx['preference'] = self.request.user.userprofile.displayPref
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = ["Serial dictatorship: early voters first", "Serial dictatorship: late voter first", "Manually allocate"]
        ctx['view_preferences'] = ["Everyone can see all votes at all times", "Everyone can see all votes", "Only show the names of voters", "Only show number of voters", "Everyone can only see his/her own vote"]
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

def addChoice(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    item_text = request.POST['choice']
    imageURL = request.POST['imageURL']
    #check for empty strings
    if item_text == "":
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # check for duplicates
    allChoices = question.item_set.all()
    for choice in allChoices:
        if item_text == choice.item_text:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # create the choice
    item = Item(question=question, item_text=item_text)
    # if the user uploaded an image or set a URL, add it to the item
    if request.FILES.get('docfile') != None:
        item.image = request.FILES.get('docfile')
    elif imageURL != '':
        item.imageURL = imageURL 
    # save the choice
    item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def deleteChoice(request, choice_id):
    item = get_object_or_404(Item, pk=choice_id)
    item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def deletePoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.delete()
    return HttpResponseRedirect(reverse('polls:index'))

def startPoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # set the poll to start
    question.status = 2
    question.save()
    # send notification email
    if question.emailStart:
        sendEmail(request, question_id, 'start')
    return HttpResponseRedirect(reverse('polls:index'))    

def stopPoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # set the status to stop
    question.status = 3
    # get winner or allocation, and save it
    if question.question_type == 1: #poll
        question.winner = getPollWinner(question)
    elif question.question_type == 2: #allocation
        allocation_serial_dictatorship(question.response_set.all())
    question.save()
    return HttpResponseRedirect(reverse('polls:index'))

def getPollWinner(question):
    all_responses = question.response_set.reverse()
    if len(all_responses) == 0:
        return ""

    (latest_responses, previous_responses) = categorizeResponses(all_responses)
    vote_results = getVoteResults(latest_responses)
    indexVoteResults = question.poll_algorithm - 1
    current_result = vote_results[indexVoteResults]
    
    winnerStr = ""
    item_set = list(question.item_set.all())
    for index, score in current_result.items():
        # index 5 uses Simplified Bucklin, where score is rank. A low score means it has a high rank (e.g. rank 1 > rank 2), so the best score is the minimum.
        # All other indices rank score from highest to lowest, so the best score would be the maximum.  
        if (score == min(current_result.values()) and indexVoteResults == 5) or (score == max(current_result.values()) and indexVoteResults != 5):
            #add a comma to separate the winners            
            if winnerStr != "":
                winnerStr += ", "
            #add the winner
            winnerStr += item_set[index].item_text
    return winnerStr
    
# view for question detail
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_order(self, ctx):
        otherUserResponses = self.object.response_set.reverse()
        preferences = []
        if len(otherUserResponses) == 0:
            return ctx['object'].item_set.all
        for resp in otherUserResponses:
            user = self.request.user
            otherUser = resp.user
            KT = getKTScore(user, otherUser)
            
            prefGraph = {}
            dictionary = get_object_or_404(Dictionary, response=resp)
            
            candMap = {}
            counter = 0
            for item in dictionary.items():
                candMap[counter] = item[0]
                counter += 1

            for cand1Index in candMap:
                tempDict = {}
                for cand2Index in candMap:
                    if cand1Index == cand2Index:
                        continue
                    
                    cand1 = candMap[cand1Index]
                    cand2 = candMap[cand2Index]
                    cand1Rank = dictionary.get(cand1)
                    cand2Rank = dictionary.get(cand2)
                    #lower number is better (i.e. rank 1 is better than rank 2)
                    if cand1Rank < cand2Rank:
                        tempDict[cand2Index] = 1
                    elif cand2Rank < cand1Rank:
                        tempDict[cand2Index] = -1
                    else:
                        tempDict[cand2Index] = 0
                prefGraph[cand1Index] = tempDict
            preferences.append(Preference(prefGraph, KT))
        pollProfile = Profile(candMap, preferences)

        pref = MechanismBorda().getCandScoresMap(pollProfile)
        l = list(sorted(pref.items(), key=lambda kv: (kv[1], kv[0])))
        final_list = []
        for p in reversed(l):
            final_list.append(candMap[p[0]])
        print(final_list)
        return final_list

    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        tempOrderStr = self.request.GET.get('order', '')
        if tempOrderStr == "null":
            ctx['items'] = self.get_order(ctx)
            return ctx
        # check if the user submitted a vote earlier and display that for modification
        if len(currentUserResponses) > 0:
            mostRecentResponse = currentUserResponses[0]
            selectionArray = []             
            for d in mostRecentResponse.dictionary_set.all():   
                selectionArray = d.sorted_values()
            ctx['currentSelection'] = selectionArray
        else:
            # no history so display the list of choices
            ctx['items'] = self.get_order(ctx)
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
       
class DependencyView(generic.DetailView):
    model = Question
    template_name = 'polls/dependency.html'
    
class DependencyDetailView(generic.DetailView):
    model = Combination
    template_name = 'polls/dependencydetail.html'
    
    def get_order(self, ctx):
        otherUserResponses = self.object.target_question.response_set.reverse()
        preferences = []
        if len(otherUserResponses) == 0:
            return self.object.target_question.item_set.all
        for resp in otherUserResponses:
            user=self.request.user
            otherUser = resp.user
            questions = Question.objects.all().filter(question_voters=otherUser).filter(question_voters=user)
            KT = 0
            num = 0
            prefGraph = {}
            dictionary = get_object_or_404(Dictionary, response=resp)
            for q in questions:
                userResponse = q.response_set.filter(user=user).reverse()
                otherUserResponse = q.response_set.filter(user=otherUser).reverse()
                if len(userResponse) > 0 and len(otherUserResponse) > 0:
                    num = num + 1
                    userResponse = get_object_or_404(Dictionary, response=userResponse[0])
                    otherUserResponse = get_object_or_404(Dictionary, response=otherUserResponse[0])
                    KT += getKendallTauScore(userResponse, otherUserResponse)
                    print(getKendallTauScore(userResponse, otherUserResponse))
            KT /= num
            if KT == 0:
                KT = .25
            else:
                KT = 1/(1 + KT)

            candMap = {}
            counter = 0
            for item in dictionary.items():
                candMap[counter] = item[0]
                counter += 1

            for cand1Index in candMap:
                tempDict = {}
                for cand2Index in candMap:
                    if cand1Index == cand2Index:
                        continue
                    
                    cand1 = candMap[cand1Index]
                    cand2 = candMap[cand2Index]
                    cand1Rank = dictionary.get(cand1)
                    cand2Rank = dictionary.get(cand2)
                    #lower number is better (i.e. rank 1 is better than rank 2)
                    if cand1Rank < cand2Rank:
                        tempDict[cand2Index] = 1
                    elif cand2Rank < cand1Rank:
                        tempDict[cand2Index] = -1
                    else:
                        tempDict[cand2Index] = 0
                prefGraph[cand1Index] = tempDict
            preferences.append(Preference(prefGraph, KT))
        pollProfile = Profile(candMap, preferences)

        pref = MechanismBorda().getCandScoresMap(pollProfile)
        l = list(sorted(pref.items(), key=lambda kv: (kv[1], kv[0])))
        final_list = []
        for p in reversed(l):
            final_list.append(candMap[p[0]])
        print(final_list)
        return final_list
    def get_context_data(self,**kwargs):
        ctx = super(DependencyDetailView, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().target_question
        currentUserResponses = self.object.target_question.response_set.filter(user=self.request.user).reverse()
        tempOrderStr = self.request.GET.get('order', '')
        if tempOrderStr == "null":
            ctx['items'] = self.get_order(ctx)
            return ctx
        if len(currentUserResponses) > 0:
            mostRecentResponse = currentUserResponses[0]
            selectionArray = []             
            for d in mostRecentResponse.dictionary_set.all():   
                selectionArray = d.sorted_values()
            ctx['currentSelection'] = selectionArray
        else:
            ctx['items'] = self.get_order(ctx)
        return ctx

def getKTScore(user, otherUser):
    KT = 0
    num = 0
    questions = Question.objects.all().filter(question_voters=otherUser).filter(question_voters=user)
    for q in questions:
        userResponse = q.response_set.filter(user=user).reverse()
        otherUserResponse = q.response_set.filter(user=otherUser).reverse()
        if len(userResponse) > 0 and len(otherUserResponse) > 0:
            num = num + 1
            userResponse = get_object_or_404(Dictionary, response=userResponse[0])
            otherUserResponse = get_object_or_404(Dictionary, response=otherUserResponse[0])
            KT += getKendallTauScore(userResponse, otherUserResponse)
            print(getKendallTauScore(userResponse, otherUserResponse))
    
    if num != 0:
        KT /= num
    if KT == 0:
        KT = .25
    else:
        KT = 1/(1 + KT)
    return KT    
    
# view for settings detail
class PollInfoView(generic.DetailView):
    model = Question
    template_name = 'polls/pollinfo.html'
    def get_context_data(self, **kwargs):
        ctx = super(PollInfoView, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = ["Allocation by time", "Manually allocate"]        
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        ctx['mostRecentResponse'] = currentUserResponses[0] if (len(currentUserResponses) > 0) else None
        ctx['history'] = currentUserResponses[1:]
        
        all_responses = self.object.response_set.reverse()
        (latest_responses, previous_responses) = categorizeResponses(all_responses)
        ctx['latest_responses'] = latest_responses
        ctx['previous_responses'] = previous_responses    
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# view for results detail
class AllocateResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/allocate_results.html'

# view for submission confirmation
class ConfirmationView(generic.DetailView):
    model = Question
    template_name = 'polls/confirmation.html'

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
        voteResults = getVoteResults(latest_responses) 
        ctx['vote_results'] = voteResults
        ctx['shade_values'] = getShadeValues(voteResults)
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['margin_victory'] = getMarginOfVictory(latest_responses)
        
        previous_winners = OldWinner.objects.all().filter(question=self.object)
        ctx['previous_winners'] = []
        for pw in previous_winners:
            obj = {}
            responses = self.object.response_set.reverse().filter(timestamp__range=[datetime.date(1899, 12, 30), pw.response.timestamp])
            (lr, pr) = categorizeResponses(responses)
            obj['title'] = str(pw)
            obj['latest_responses'] = lr
            obj['previous_responses'] = pr
            obj['vote_results'] = getVoteResults(lr)
            obj['margin_victory'] = getMarginOfVictory(lr)
            ctx['previous_winners'].append(obj)
        return ctx

# get a list of algorithms supported by the system
def getListPollAlgorithms():
    return ["Plurality", "Borda", "Veto", "K-approval (k = 3)", "Simplified Bucklin", "Copeland", "Maximin"]

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
    scoreVectorList.append(MechanismPlurality().getCandScoresMap(pollProfile))  
    scoreVectorList.append(MechanismBorda().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismVeto().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismKApproval(3).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismSimplifiedBucklin().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismCopeland(1).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismMaximin().getCandScoresMap(pollProfile))
    
    return scoreVectorList

# return lighter (+lum) or darker (-lum) color as a hex string
# pass original hex string and luminosity factor, e.g. -0.1 = 10% darker
def colorLuminance(hexVal, lum):
    #convert to decimal and change luminosity
    rgb = "#"
    for i in range(0, 3): 
        c = int(hexVal[i * 2 : i * 2 + 2], 16)
        c = round(min(max(0, c + (c * float(lum))), 255))
        c = hex(int(c))
        rgb += ("00" + str(c))[len(str(c)):]
    return rgb

# get a range of colors from green to red 
def getShadeValues(scoreVectorList):
    shadeValues = []

    for row in scoreVectorList:
        sortedRow = sorted(set(list(row.values())))
        highestRank = len(sortedRow) - 1

        newRow = []
        greenColor = "6cbf6c"
        redColor = "dc6460"
        for index in row:
            rank = sortedRow.index(row[index])

            if highestRank == 0:
                # must be the winner
                newRow.append("#" + greenColor)
            else:
                # at the midpoint, change colors
                midRank = highestRank / 2
                # color is a hex value
                colorStr = ""
                # make the colors closer to the end darker (lower value) and toward the middle lighter (higher value) 
                luminance = 0
                if midRank != 0:
                    luminance = 1 - (abs(midRank - rank) / float(midRank))
                    luminance /= 2.0

                #the 5th row is Simplified Bucklin (lower score is better so reverse the colorings for this row)
                counter = len(shadeValues)
                # check if the ranking is above or below the midpoint and assign colors accordingly
                if (rank <= midRank and counter != 4) or (rank > midRank and counter == 4):
                    colorStr = colorLuminance(redColor, luminance)
                else:
                    colorStr = colorLuminance(greenColor, luminance)

                newRow.append(colorStr)

        shadeValues.append(newRow)
    return shadeValues

# find the minimum number of votes needed to change the poll results
def getMarginOfVictory(latest_responses):
    pollProfile = getPollProfile(latest_responses)
    if pollProfile == None:
        return []
    
    #make sure no ties or incomplete results are in the votes
    if pollProfile.getElecType() != "soc":
        return []
    print(MechanismPlurality().getMov(pollProfile))
    marginList = []
    marginList.append(MechanismPlurality().getMov(pollProfile))  
    marginList.append(MechanismBorda().getMov(pollProfile))
    marginList.append(MechanismVeto().getMov(pollProfile))
    marginList.append(MechanismKApproval(3).getMov(pollProfile))
    #if len(latest_responses) > 1:
     #   marginList.append(MechanismSimplifiedBucklin().getMov(pollProfile))
    marginList.append("-")
    return marginList

#function to add voter to voter list (invite only)
def addVoter(request, question_id):
    question    = get_object_or_404(Question, pk=question_id)
    creator_obj = User.objects.get(id=question.question_owner_id)

    newVoters = request.POST.getlist('voters')
    # send an invitation email
    email = request.POST.get('email') == 'email'
    question.emailInvite = email
    question.save()
    if email:
        sendEmail(request, question_id, 'invite')
    # add each voter to the question by username
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.add(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#remove voters from the list
def removeVoter(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    newVoters = request.POST.getlist('voters')
    email = request.POST.get('email') == 'email'
    question.emailDelete = email
    question.save()
    if email:
        sendEmail(request, question_id, 'remove')   
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.remove(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def setInitialSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.poll_algorithm = request.POST['pollpreferences']
    question.display_pref = request.POST['viewpreferences']
    question.save()
    return HttpResponseRedirect(reverse('polls:index'))

def setAlgorithm(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.poll_algorithm = request.POST['pollpreferences']
    question.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def setVisibility(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    displayChoice = request.POST['viewpreferences']
    if displayChoice == "always":
        question.display_pref = 0
    elif displayChoice == "allpermit":
        question.display_pref = 1
    elif displayChoice == "voternames":
        question.display_pref = 2
    elif displayChoice == "justnumber":
        question.display_pref = 3
    else:
        question.display_pref = 4
    question.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# function to process student submission
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # get the preference order
    orderStr = request.POST["pref_order"]
    prefOrder = []    
    if orderStr != "":
        prefOrder = orderStr.split(",")
        # the user must rank all preferences
        if len(prefOrder) != len(question.item_set.all()):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # the user must rank all preferences
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    # make Response object to store data
    response = Response(question=question, user=request.user, timestamp=timezone.now())
    response.save()
    d = response.dictionary_set.create(name = response.user.username + " Preferences")

    # find ranking student gave for each item under the question
    item_num = 1
    for item in question.item_set.all():
        arrayIndex = prefOrder.index("item" + str(item_num))
        if arrayIndex == -1:
            # set value to lowest possible rank
            d[item] = question.item_set.all().count()
        else:
            # add 1 to array index, since rank starts at 1
            rank = (prefOrder.index("item" + str(item_num))) + 1
            # add pref to response dict
            d[item] = rank
        d.save()
        item_num += 1

    #get current winner
    old_winner = OldWinner(question=question, response=response)
    old_winner.save()

    return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))

def dependencyRedirect(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.multipollquestion_set.all()[0].order == question.multipoll_set.all()[0].status-1:
        return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))
    else:
        return HttpResponseRedirect(reverse('polls:dependencyview', args=(question.id,)))

def chooseDependency(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    dependencies = []
    l = request.POST.getlist('polls')
    for poll in l:
        i = int(poll)
        dependencies.append(poll)
    combination = Combination(target_question=question, user=request.user)
    combination.save()
    if len(dependencies) > 0:
        for poll in dependencies:
            combination.dependent_questions.add(poll)
            combination.save()
    return HttpResponseRedirect(reverse('polls:dependencydetail', args=(combination.id,)))
    
def assignPreference(request, combination_id):
    combination = get_object_or_404(Combination, pk=combination_id)
    question = get_object_or_404(Question, pk=combination.target_question.id)
    for poll in combination.dependent_questions.all():
        s = str(poll.id)
        itemtxt = request.POST[s]
        item = poll.item_set.get(item_text=itemtxt)
        combination.dependencies.add(item.id)
        combination.save()
    orderStr = request.POST["pref_order"]
    prefOrder = []    
    if orderStr != "":
        prefOrder = orderStr.split(",")
        # the user must rank all preferences
        if len(prefOrder) != len(question.item_set.all()):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # the user must rank all preferences
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # make Response object to store data
    response = Response( user=request.user, timestamp=timezone.now())
    response.save()
    combination.response = response
    combination.save()
    d = response.dictionary_set.create(name = response.user.username + " Predicting Preferences")

    # find ranking student gave for each item under the question
    item_num = 1
    for item in question.item_set.all():
        arrayIndex = prefOrder.index("item" + str(item_num))
        if arrayIndex == -1:
            # set value to lowest possible rank
            d[item] = question.item_set.all().count()
        else:
            # add 1 to array index, since rank starts at 1
            rank = (prefOrder.index("item" + str(item_num))) + 1
            # add pref to response dict
            d[item] = rank
        d.save()
        item_num += 1
    return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))