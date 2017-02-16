import datetime
import os
import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from prefpy.mechanism import *
from prefpy.allocation_mechanism import *
from prefpy.gmm_mixpl import *
from .email import EmailThread, setupEmail
from groups.models import *
from django.conf import settings
from multipolls.models import *

import json
import threading
import itertools
import django_rq

# view for homepage - index of questions & results
class IndexView(generic.ListView):
    template_name = 'polls/index2.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')

class RegularPollsView(generic.ListView):
    template_name = 'polls/regular_polls.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all()
    def get_context_data(self, **kwargs):
        ctx = super(RegularPollsView, self).get_context_data(**kwargs)
        # sort the lists by date (most recent should be at the top)
        ctx['polls_created'] = Question.objects.filter(question_owner = self.request.user, m_poll = False).order_by('-pub_date')
        ctx['polls_participated'] = self.request.user.poll_participated.filter(m_poll = False).exclude(question_owner = self.request.user).order_by('-pub_date')
        return ctx

# the original query will return data from earliest to latest
# reverse the list so that the data is from latest to earliest
def reverseListOrder(query):
    listQuery = list(query)
    listQuery.reverse()
    return listQuery

class MultiPollsView(generic.ListView):
    template_name = 'polls/m_polls.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all()
    def get_context_data(self, **kwargs):
        ctx = super(MultiPollsView, self).get_context_data(**kwargs)
        # sort the list by date
        ctx['multipolls_created'] = reverseListOrder(MultiPoll.objects.filter(owner = self.request.user))
        ctx['multipolls_participated'] = reverseListOrder(self.request.user.multipoll_participated.exclude(owner = self.request.user))
        return ctx

# guest homepage view
class MainView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'
    def get_queryset(self):
        return Question.objects.all().order_by('-pub_date')
    def get_context_data(self, **kwargs):
        ctx = super(MainView, self).get_context_data(**kwargs)
        # sort the list by date
        ctx['question']=Question.objects.first()
        ctx['voting_question'] = Question.objects.filter(question_text="Demo").first()
        ctx['preference'] = 1
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = getAllocMethods()
        ctx['view_preferences'] = getViewPreferences()
        
        return ctx

# demo for voting page in main page
# view for question detail
class DemoView(generic.DetailView):
    model = Question
    template_name = 'polls/demo.html'

    def get_order(self, ctx):
        otherUserResponses = self.object.response_set.reverse()
        defaultOrder = ctx['object'].item_set.all()
        #random.shuffle(defaultOrder)
        return defaultOrder
        #return getRecommendedOrder(otherUserResponses, self.request, defaultOrder)

    def get_context_data(self, **kwargs):
        ctx = super(DemoView, self).get_context_data(**kwargs)
        ctx['items'] = self.get_order(ctx)
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

        
# step 1: the intial question object will be created. 
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
            emailStop=request.user.userprofile.emailStop, creator_pref=1)
        if request.FILES.get('docfile') != None:
            question.image = request.FILES.get('docfile')
        elif imageURL != '':
            question.imageURL = imageURL 
        question.question_type = questionType
        question.save()
        setupEmail(question)
        return HttpResponseRedirect(reverse('polls:AddStep2', args=(question.id,)))
    return render_to_response('polls/add_step1.html', {}, context)

# step 2: the owner adds choices to a poll
class AddStep2View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step2.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep2View, self).get_context_data(**kwargs)
        ctx['items'] = self.object.item_set.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# step 3: the owner invites voters and groups to a poll
class AddStep3View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step3.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep3View, self).get_context_data(**kwargs)
        ctx['users'] = User.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# step 4: the owner selects the type of poll and other settings    
class AddStep4View(generic.DetailView):
    model = Question
    template_name = 'polls/add_step4.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep4View, self).get_context_data(**kwargs)
        ctx['preference'] = self.request.user.userprofile.displayPref
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = getAllocMethods()
        ctx['view_preferences'] = getViewPreferences()
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# Add a single choice to a poll.
# - A choice must contain text
# - No duplicate choices (text can't be the same) 
# - The user can add an image to the choice, but images are optional
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
    item = Item(question=question, item_text=item_text, timestamp=timezone.now())
    
    # if the user uploaded an image or set a URL, add it to the item
    if request.FILES.get('docfile') != None:
        item.image = request.FILES.get('docfile')
    elif imageURL != '':
        item.imageURL = imageURL 
    
    # save the choice
    item.save()
    request.session['setting'] = 0
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editChoice(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    for item in question.item_set.all():
        new_text = request.POST["item"+str(item.id)]
        item_desc = request.POST["itemdescription"+str(item.id)]
        imageURL = request.POST["imageURL"+str(item.id)]
        if item_desc != "":
            item.item_description = item_desc
        if request.FILES.get("docfile"+str(item.id)) != None:
            item.image = request.FILES.get("docfile"+str(item.id))
        elif imageURL != "":
            item.imageURL = imageURL
        item.item_text = new_text
        item.save()
    request.session['setting'] = 0
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def editBasicInfo(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    new_title = request.POST["title"]
    new_desc = request.POST["desc"]
    question.question_text = new_title
    question.question_desc = new_desc    
    question.save()
    request.session['setting'] = 0
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# remove a choice from the poll. 
# deleting choices should only be done before the poll starts
def deleteChoice(request, choice_id):
    item = get_object_or_404(Item, pk=choice_id)
    item.delete()
    request.session['setting'] = 0
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# permanently erase a poll and all its information and settings
def deletePoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # check to make sure the current user is the owner
    if request.user != question.question_owner:
        return HttpResponseRedirect(reverse('polls:index'))    
    
    question.delete()
    return HttpResponseRedirect(reverse('polls:index'))

# the voter can opt out of a poll at any time 
def quitPoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # notify the user if this option is checked
    if request.user.userprofile.emailDelete:
        email_class = EmailThread(request, question_id, 'remove')
        email_class.start()
        
    # remove from the voter list
    question.question_voters.remove(request.user)
    question.save()

    return HttpResponseRedirect(reverse('polls:regular_polls'))

# when a poll starts, users can cast votes at any time. 
# however, the owner won't be able to remove voters or choices
def startPoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # check to make sure the owner started the poll
    if request.user != question.question_owner:
        return HttpResponseRedirect(reverse('polls:index'))
    
    # set the poll to start
    question.status = 2
    question.save()
    
    # send notification email
    if question.emailStart:
        email_class = EmailThread(request, question_id, 'start')
        email_class.start()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

# when a poll stops, users can no longer cast votes
# the final results will be calculated and displayed
def stopPoll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # check to make sure the owner stopped the poll
    if request.user != question.question_owner:
        return HttpResponseRedirect(reverse('polls:index'))    
    
    # set the status to stop
    question.status = 3
    # get winner or allocation, and save it
    if question.question_type == 1: #poll
        question.winner = getPollWinner(question)
    elif question.question_type == 2: #allocation
        getFinalAllocation(question)
    question.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# find the winner(s) using the polling algorithm selected earlier 
# Question question
# return String winnerStr
def getPollWinner(question):
    all_responses = question.response_set.filter(active=1).order_by('-timestamp')
    if len(all_responses) == 0:
        return ""

    (latest_responses, previous_responses) = categorizeResponses(all_responses)
    candMap = getCandidateMapFromList(list(question.item_set.all()))
    vote_results, mixtures = getVoteResults(latest_responses,candMap)
    indexVoteResults = question.poll_algorithm - 1
    current_result = vote_results[indexVoteResults]

    winnerStr = ""
    
    #item_set = getCandidateMap(latest_responses[0])
    for index, score in current_result.items():
        # index 5 uses Simplified Bucklin, where score is rank. A low score means it has a high rank (e.g. rank 1 > rank 2), so the best score is the minimum.
        # All other indices rank score from highest to lowest, so the best score would be the maximum.  
        if (score == min(current_result.values()) and indexVoteResults == 5) or (score == max(current_result.values()) and indexVoteResults != 5):
            #add a comma to separate the winners            
            if winnerStr != "":
                winnerStr += ", "
            #add the winner
            winnerStr += candMap[index].item_text
            
    if hasattr(question, 'finalresult'):
        question.finalresult.delete()
    result = FinalResult(question=question,timestamp=timezone.now(),result_string="",mov_string="",cand_num=question.item_set.all().count(),node_string="",edge_string="",shade_string="")
    resultstr = ""
    movstr = ""
    nodestr = ""
    edgestr = ""
    shadestr = ""
    mov = getMarginOfVictory(latest_responses,candMap)
    for x in range(0,len(vote_results)):
        for key,value in vote_results[x].items():
            resultstr += str(value)
            resultstr += ","
    for x in range(0,len(mov)):
        movstr += str(mov[x])
        movstr += ","
    resultstr = resultstr[:-1]
    movstr = movstr[:-1]
    (nodes, edges) = parseWmg(latest_responses,candMap)
    for node in nodes:
        for k,v in node.items():
            nodestr += k + "," + str(v) + ";"
        nodestr += "|"
    nodestr = nodestr[:-2]
    for edge in edges:
        for k,v in edge.items():
            edgestr += k + "," + str(v) + ";"
        edgestr += "|"
    edgestr = edgestr[:-2]
    shadevalues = getShadeValues(vote_results)
    for x in shadevalues:
        for y in x:
            shadestr += y + ";"
        shadestr += "|"
    shadestr = shadestr[:-2]
    result.result_string = resultstr
    result.mov_string = movstr
    result.node_string = nodestr
    result.edge_string = edgestr
    result.shade_string = shadestr
    result.save()
    return winnerStr
    
    
#Interpret result into strings that can be shown on the result page
#FinalResult finalresult
#List<List<String>>
def interpretResult(finalresult):
    candnum = finalresult.cand_num
    resultstr = finalresult.result_string
    movstr = finalresult.mov_string
    shadestr = finalresult.shade_string
    nodestr = finalresult.node_string
    edgestr = finalresult.edge_string
    resultlist = resultstr.split(",")
    movlist = movstr.split(",")
    tempResults = []
    algonum = len(getListPollAlgorithms())
    if len(resultlist) > 0:
        for x in range(0,algonum):
            tempList = []
            for y in range(x*candnum, (x+1)*candnum):
                tempList.append(resultlist[y])
            tempResults.append(tempList)
    tempMargin = []
    for margin in movlist:
        tempMargin.append(margin)
    tempShades = []
    shadelist = shadestr.split(";|")
    for item in shadelist:
        tempShades.append(item.split(";"))
    tempNodes = []
    nodelist = nodestr.split(";|")
    for node in nodelist:
        data = {}
        l = node.split(";")
        for item in l:
            tup = item.split(",")
            data[tup[0]] = tup[1]
        tempNodes.append(data)
    tempEdges = []
    edgelist = edgestr.split(";|")
    for edge in edgelist:
        data = {}
        l = edge.split(";")
        for item in l:
            tup = item.split(",")
            data[tup[0]] = tup[1]
        tempEdges.append(data)
    return [tempResults, tempMargin, tempShades, tempNodes, tempEdges]
    
def recalculateResult(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    getPollWinner(question)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

# check whether the user clicked 'reset' when ordering preferences
def isPrefReset(request):
    # reset link would have '?order=null' at the end
    orderStr = request.GET.get('order', '')
    if orderStr == "null":
        return True
    return False 

# given a list of responses, return the response's selection data
# List<Response> mostRecentResponse
# return List<List<(Item, int)>> array
def getCurrentSelection(mostRecentResponse):
    responseDict = {}
    if mostRecentResponse.dictionary_set.all().count() > 0:
        responseDict = mostRecentResponse.dictionary_set.all()[0]
    else:
        responseDict = buildResponseDict(mostRecentResponse,mostRecentResponse.question,getPrefOrder(mostRecentResponse.resp_str, mostRecentResponse.question))
    rd = responseDict
    array = []
    for itr in range(mostRecentResponse.question.item_set.all().count()):
        array.append([])
    for itr in rd:
        array[rd[itr] - 1].append(itr)
    return array

# view for question detail
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_order(self, ctx):
        otherUserResponses = self.object.response_set.reverse()
        defaultOrder = list(ctx['object'].item_set.all())
        random.shuffle(defaultOrder)
        return defaultOrder
        #commented out to improve performance
        #return getRecommendedOrder(otherUserResponses, self.request, defaultOrder)

    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)
        ctx['lastcomment'] = ""
        
        #Case for anonymous user
        if self.request.user.get_username() == "":
            if isPrefReset(self.request):
                ctx['items'] = self.object.item_set.all()
                return ctx
            # check the anonymous voter
            if 'anonymousvoter' in self.request.session and 'anonymousid' in self.request.session:
                # sort the responses from latest to earliest
                currentAnonymousResponses = self.object.response_set.filter(anonymous_id = self.request.session['anonymousid']).reverse()
                if len(currentAnonymousResponses) > 0:
                    # get the voter's most recent selection
                    mostRecentAnonymousResponse = currentAnonymousResponses[0]
                    if mostRecentAnonymousResponse.comment:
                        ctx['lastcomment'] = mostRecentAnonymousResponse.comment
                    ctx['currentSelection'] = getCurrentSelection(currentAnonymousResponses[0])
            else:
                # load choices in the default order
                ctx['items'] = self.object.item_set.all()
            return ctx

        # Get the responses for the current logged-in user from latest to earliest
        currentUserResponses = self.object.response_set.filter(user=self.request.user).reverse()
        
        if len(currentUserResponses) > 0:
            if currentUserResponses[0].comment:
                ctx['lastcomment'] = currentUserResponses[0].comment

        # reset button
        if isPrefReset(self.request):
            ctx['items'] = self.get_order(ctx)
            return ctx
        
        # check if the user submitted a vote earlier and display that for modification
        if len(currentUserResponses) > 0: 
            ctx['currentSelection'] = getCurrentSelection(currentUserResponses[0])
            items = []
            for item in ctx['currentSelection']:
                for i in item:
                    items.append(i)
            ctx['items'] = items
            ctx['itr'] = itertools.count(1, 1)
        else:
            # no history so display the list of choices
            ctx['items'] = self.get_order(ctx)
        return ctx
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# view for settings detail
class PollInfoView(generic.DetailView):
    model = Question
    template_name = 'polls/pollinfo.html'
    def get_context_data(self, **kwargs):
        ctx = super(PollInfoView, self).get_context_data(**kwargs)
        emailInvite = Email.objects.filter(question=self.object, type=1)
        if len(emailInvite) == 1:
            setupEmail(self.object)
        if Email.objects.filter(question=self.object).count() > 0:
            ctx['emailInvite'] = Email.objects.filter(question=self.object, type=1)[0]
            ctx['emailDelete'] = Email.objects.filter(question=self.object, type=2)[0]
            ctx['emailStart'] = Email.objects.filter(question=self.object, type=3)[0]
            ctx['emailStop'] = Email.objects.filter(question=self.object, type=4)[0]
        ctx['users'] = User.objects.all()
        ctx['items'] = self.object.item_set.all()
        ctx['groups'] = Group.objects.all()
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = getAllocMethods()
        
        # display this user's history
        currentUserResponses = self.object.response_set.filter(user=self.request.user,active=1).order_by('-timestamp')
        ctx['user_latest_responses'] = getSelectionList([currentUserResponses[0]]) if (len(currentUserResponses) > 0) else None
        ctx['user_previous_responses'] = getSelectionList(currentUserResponses[1:])
        
        # get history of all users
        all_responses = self.object.response_set.filter(active=1).order_by('-timestamp')
        (latest_responses, previous_responses) = categorizeResponses(all_responses)
        ctx['latest_responses'] = getSelectionList(latest_responses)
        ctx['previous_responses'] = getSelectionList(previous_responses)    
        
        # get deleted votes
        deleted_responses = self.object.response_set.reverse().filter(active=0).order_by('-timestamp')
        (latest_deleted_responses, previous_deleted_responses) = categorizeResponses(deleted_responses)
        ctx['latest_deleted_responses'] = getSelectionList(latest_deleted_responses)
        ctx[''] = getSelectionList(previous_deleted_responses)
        
        if self.object.question_voters.all().count() > 0:
            progressPercentage = len(latest_responses) / self.object.question_voters.all().count() * 100
            ctx['progressPercentage'] = progressPercentage
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

# view that displays vote results using various algorithms
class VoteResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/vote_rule.html'
    def get_context_data(self, **kwargs):
        ctx = super(VoteResultsView, self).get_context_data(**kwargs)
        
        candMap = getCandidateMapFromList(list(self.object.item_set.all()))
        ctx['cand_map'] = candMap# if (len(latest_responses) > 0) else None
        ctx['poll_algorithms'] = getListPollAlgorithms()
        if hasattr(self.object, 'finalresult'):
            final_result = self.object.finalresult
            l = interpretResult(final_result)
            ctx['vote_results'] = l[0]
            ctx['margin_victory'] = l[1]
            ctx['shade_values'] = l[2]
            ctx['wmg_nodes'] = l[3]
            ctx['wmg_edges'] = l[4]
        else:
            all_responses = self.object.response_set.filter(active=1).order_by('-timestamp')
            (latest_responses, previous_responses) = categorizeResponses(all_responses)
            voteResults, mixtures = getVoteResults(latest_responses,candMap) 
            resultlist = []
            for r in voteResults:
                resultlist.append(r.values())
            ctx['vote_results'] = resultlist
            ctx['shade_values'] = getShadeValues(voteResults)
            (nodes, edges) = parseWmg(latest_responses,candMap)
            ctx['wmg_nodes'] = nodes
            ctx['wmg_edges'] = edges
            
            ctx['margin_victory'] = getMarginOfVictory(latest_responses,candMap)
            #ctx['mixtures_pl'] = mixtures[0]
            
        previous_results = self.object.voteresult_set.all()
        ctx['previous_winners'] = []
        for pw in previous_results:
            obj = {}
            obj['title'] = str(pw.timestamp.time())
            candnum = pw.cand_num
            resultstr = pw.result_string
            movstr = pw.mov_string
            if resultstr == "" and movstr == "":
                continue
            resultlist = resultstr.split(",")
            movlist = movstr.split(",")
            tempResults = []
            algonum = len(getListPollAlgorithms())
            if len(resultlist) > 0:
                for x in range(0,algonum):
                    tempList = []
                    for y in range(x*candnum, (x+1)*candnum):
                        tempList.append(resultlist[y])
                    tempResults.append(tempList)
            obj['vote_results'] = tempResults
            tempMargin = []
            for margin in movlist:
                tempMargin.append(margin)
            obj['margin_victory'] = tempMargin
            ctx['previous_winners'].append(obj)
        return ctx

# get a list of algorithms supported by the system
# return List<String>
def getListPollAlgorithms():
    return ["Plurality", "Borda", "Veto", "K-approval (k = 3)", "Simplified Bucklin", "Copeland", "Maximin"]

# get a list of allocation methods
# return List<String>
def getAllocMethods():
    return ["Serial dictatorship: early voters first", "Serial dictatorship: late voter first", "Manually allocate"]

# get a list of visibility settings
# return List<String>
def getViewPreferences():
    return ["Everyone can see all votes at all times", "Everyone can see all votes", "Only show the names of voters", "Only show number of voters", "Everyone can only see his/her own vote"]

# build a graph of nodes and edges from a 2d dictionary
# List<Response> latest_responses
# return (List<Dict> nodes, List<Dict> edges)
def parseWmg(latest_responses,candMap):
    pollProfile = getPollProfile(latest_responses,candMap)
    if pollProfile == None:
        return ([], [])
   
    #make sure no incomplete results are in the votes
    if pollProfile.getElecType() != "soc" and pollProfile.getElecType() != "toc":
        return ([], [])  

    # make sure there's at least one response
    if len(latest_responses) == 0:
        return ([], [])
        
    # get nodes (the options)
    nodes = []
    for rowIndex in candMap:
        data = {}
        data['id'] = rowIndex
        data['value'] = 1
        data['label'] = candMap[rowIndex].item_text
        nodes.append(data)

    # get edges from the weighted majority graph
    wmg = pollProfile.getWmg()
    edges = []
    for rowIndex in wmg:
        row = wmg[rowIndex]
        for colIndex in row:
            value = row[colIndex]
            if value > 0:
                data = {}
                data['from'] = rowIndex
                data['to'] = colIndex
                data['value'] = value
                data['title'] = str(value)
                edges.append(data)

    return (nodes, edges)

# format a list of votes to account for ties
def getSelectionList(responseList):
    selectList = []
    for response in responseList:
        selectList.append((response, getCurrentSelection(response)))
    return selectList

#separate the user votes into two categories: (1)most recent (2)previous history
# List<Response> all_responses
# return (List<Response> latest_responses, List<Response> previous_responses)
def categorizeResponses(all_responses):
    latest_responses = []
    previous_responses = []
    
    if len(all_responses) > 0:
        #the first response must be the most recent 
        latest_responses.append(all_responses[0])   
    
    others = all_responses[1:]
    
    #the outer loop goes through all the responses
    for response1 in others:
        #for anonymous users, check anonymous name instead of username
        if response1.user == None:
            add = True
            for response2 in latest_responses:
                if response1.anonymous_voter and response2.anonymous_voter:
                    if response1.anonymous_id == response2.anonymous_id:
                        add = False
                        previous_responses.append(response1)
                        break
            if add:
                latest_responses.append(response1)  
                    
        else:
            add = True
            #check if the user has voted multiple times
            for response2 in latest_responses:
                if not response2.user == None:
                    if response1.user.username == response2.user.username:
                        add = False
                        previous_responses.append(response1)
                        break

            #this is the most recent vote
            if add:
                latest_responses.append(response1)   
    
    return (latest_responses, previous_responses)

# get a list of options for this poll
# Response response
# return Dict<int, Item> candMap
def getCandidateMap(response):
    d = {}
    if response.dictionary_set.all().count() > 0:
        d = Dictionary.objects.get(response=response)
    else:
        d = buildResponseDict(response,response.question,getPrefOrder(response.resp_str, response.question))
    candMap = {}

    counter = 0
    for item in d.items():
        candMap[counter] = item[0]
        counter += 1
    return candMap
def getCandidateMapFromList(candlist):
    candMap = {}
    counter = 0
    for item in candlist:
        candMap[counter] = item
        counter += 1
    return candMap
#convert a user's preference into a 2d map
# Response response
# return Dict<int, Dict<int, int>> prefGraph
def getPreferenceGraph(response,candMap):
    prefGraph = {}
    dictionary = {}
    if response.dictionary_set.all().count() > 0:
        dictionary = Dictionary.objects.get(response=response)
    else:
        dictionary = buildResponseDict(response,response.question,getPrefOrder(response.resp_str, response.question))

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

    return prefGraph

# initialize a profile object using all the preferences
# List<Response> latest_responses
# return Profile object
def getPollProfile(latest_responses,candMap):
    if len(latest_responses) == 0:
        return None
    
    prefList = []
    for response in latest_responses:
        prefGraph = getPreferenceGraph(response,candMap)
        userPref = Preference(prefGraph)
        prefList.append(userPref)
    return Profile(candMap, prefList)

#calculate the results of the vote using different algorithms
# List<Response> latest_responses
# return a List<List<Double>>
def getVoteResults(latest_responses,candMap):
    pollProfile = getPollProfile(latest_responses,candMap)
    if pollProfile == None:
        return []

    #make sure no incomplete results are in the votes
    if pollProfile.getElecType() != "soc" and pollProfile.getElecType() != "toc":
        return []

    scoreVectorList = []
    scoreVectorList.append(MechanismPlurality().getCandScoresMap(pollProfile))  
    scoreVectorList.append(MechanismBorda().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismVeto().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismKApproval(3).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismSimplifiedBucklin().getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismCopeland(1).getCandScoresMap(pollProfile))
    scoreVectorList.append(MechanismMaximin().getCandScoresMap(pollProfile))
    #gmm = GMMMixPLAggregator(list(pollProfile.candMap.values()), use_matlab=False)
    
    return scoreVectorList, [[.1] * 10]#gmm.aggregate(pollProfile.getOrderVectors(), algorithm="top3_full", epsilon=.1, max_iters=10, approx_step=.1)
    
def calculatePreviousResults(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.voteresult_set.clear()
    candMap = getCandidateMapFromList(list(question.item_set.all()))
    previous_winners = question.oldwinner_set.all()
    for pw in previous_winners:
        
        result = VoteResult(question=question,timestamp=pw.response.timestamp,result_string="",mov_string="",cand_num=question.item_set.all().count())
        result.save()
        resultstr = ""
        movstr = ""
        responses = question.response_set.reverse().filter(timestamp__range=[datetime.date(1899, 12, 30), pw.response.timestamp],active=1)
        (lr, pr) = categorizeResponses(responses)
        scorelist, mixtures = getVoteResults(lr,candMap)
        mov = getMarginOfVictory(lr,candMap)
        for x in range(0,len(scorelist)):
            for key,value in scorelist[x].items():
                resultstr += str(value)
                resultstr += ","
        for x in range(0,len(mov)):
            movstr += str(mov[x])
            movstr += ","
        resultstr = resultstr[:-1]
        movstr = movstr[:-1]
        result.result_string = resultstr
        result.mov_string = movstr
        result.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

# return lighter (+lum) or darker (-lum) color as a hex string
# pass original hex string and luminosity factor, e.g. -0.1 = 10% darker
# String hexVal
# double lum
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
# List<int> scoreVectorList
# return a List<List<String>> shadeValues
def getShadeValues(scoreVectorList):
    shadeValues = []

    for row in scoreVectorList:
        sortedRow = sorted(set(list(row.values())))
        highestRank = len(sortedRow) - 1

        newRow = []
        greenColor = "6cbf6c"
        whiteColor = "ffffff"
        for index in row:
            rank = sortedRow.index(row[index])

            if highestRank == 0:
                # must be the winner
                newRow.append("#" + greenColor)
                continue

            # make the colors closer to the left lighter (higher value) and toward the right darker (lower value) 
            
            #the 5th row is Simplified Bucklin (lower score is better so reverse the colorings for this row)
            counter = len(shadeValues)
            if counter != 4:
                luminance = 1 - rank / float(highestRank)
            else:
                luminance = rank / float(highestRank)
                
            # set lowest rank to white
            if luminance == 1:
                newRow.append("#" + whiteColor)
                continue
            if luminance <= 0.5:
                luminance /= 2.0
            
            newRow.append(colorLuminance(greenColor, luminance))

        shadeValues.append(newRow)
    return shadeValues

# find the minimum number of votes needed to change the poll results
# List<Response> latest_responses
# return List<int> marginList
def getMarginOfVictory(latest_responses,candMap):
    pollProfile = getPollProfile(latest_responses,candMap)
    if pollProfile == None:
        return []
    
    #make sure no incomplete results are in the votes
    if pollProfile.getElecType() != "soc" and pollProfile.getElecType() != "toc":
        return []
    marginList = []
    marginList.append(MechanismPlurality().getMov(pollProfile))  
    marginList.append(MechanismBorda().getMov(pollProfile))
    marginList.append(MechanismVeto().getMov(pollProfile))
    marginList.append(MechanismKApproval(3).getMov(pollProfile))
    #if len(latest_responses) > 1:
     #   marginList.append(MechanismSimplifiedBucklin().getMov(pollProfile))
    #marginList.append("-")
    return marginList

# used to help find the recommended order
# User user
# User otherUser
# return double KT
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
    
    if num != 0:
        KT /= num
    if KT == 0:
        KT = .25
    else:
        KT = 1/(1 + KT)
    return KT    

# use other responses to recommend a response order for you
# responses are sorted from latest to earliest
# List<Response> response
# request request
# List<Item> defaultOrder
# return List<Item> final_list
def getRecommendedOrder(otherUserResponses, request, defaultOrder):  
    # no responses
    if len(otherUserResponses) == 0:
        return defaultOrder
    
    # if the poll owner added more choices during the poll, then reset using the default order
    itemsLastResponse = len(getCandidateMap(otherUserResponses[0])) 
    itemsCurrent = defaultOrder.count()
    if itemsLastResponse != itemsCurrent:
        return defaultOrder    
    
    # iterate through all the responses
    preferences = []
    for resp in otherUserResponses:
        user = request.user
        otherUser = resp.user
        
        # get current user and other user preferences
        KT = getKTScore(user, otherUser)
        prefGraph = getPreferenceGraph(resp,candMap)
        preferences.append(Preference(prefGraph, KT))
    
    candMap = getCandidateMap(otherUserResponses[0])        
    pollProfile = Profile(candMap, preferences)
    
    # incomplete answers 
    if pollProfile.getElecType() != "soc" and pollProfile.getElecType() != "toc":
        return defaultOrder

    # return the order based off of ranking 
    pref = MechanismBorda().getCandScoresMap(pollProfile)
    l = list(sorted(pref.items(), key=lambda kv: (kv[1], kv[0])))
    final_list = []
    for p in reversed(l):
        final_list.append(candMap[p[0]])
    return final_list    
 
# function to add voter to voter list (invite only)
# can invite new voters at any time
def addVoter(request, question_id):
    question    = get_object_or_404(Question, pk=question_id)
    creator_obj = User.objects.get(id=question.question_owner_id)

    newVoters = request.POST.getlist('voters')
    # send an invitation email 
    email = request.POST.get('email') == 'email'
    question.emailInvite = email
    question.save()
    if email:
        email_class = EmailThread(request, question_id, 'invite')
        email_class.start()
    # add each voter to the question by username
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.add(voterObj.id)
    request.session['setting'] = 1

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# remove voters from a poll.
# should only be done before a poll starts
def removeVoter(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    newVoters = request.POST.getlist('voters')
    email = request.POST.get('email') == 'email'
    question.emailDelete = email
    question.save()
    if email:
        email_class = EmailThread(request, question_id, 'remove')
        email_class.start()   
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        question.question_voters.remove(voterObj.id)
    request.session['setting'] = 1
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# called when creating the poll
def setInitialSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.poll_algorithm = request.POST['pollpreferences']
    question.display_pref = request.POST['viewpreferences']
    openstring = request.POST['openpoll']
    if openstring == "anon":
        question.open = 1
    elif openstring == "invite":
        question.open = 0
    else:
        question.open = 2
    question.save()
    return HttpResponseRedirect(reverse('polls:regular_polls'))

# set algorithms and visibility
def setPollingSettings(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # set the poll algorithm or allocation method using an integer
    if 'pollpreferences' in request.POST:
        question.poll_algorithm = request.POST['pollpreferences']
    
    # set the visibility settings, how much information should be shown to the user
    # options range from showing everything (most visibility) to showing only the user's vote (least visibility)        
    displayChoice = request.POST['viewpreferences']
    if displayChoice == "always":
        question.display_pref = 0
    elif displayChoice == "allpermit":
        question.display_pref = 1
    elif displayChoice == "voternames":
        question.display_pref = 2
    elif displayChoice == "justnumber":
        question.display_pref = 3
    elif displayChoice == "nothing":
        question.display_pref = 4
    else:
        question.display_pref = 5
    creatorChoice = request.POST['creatorpreferences']
    if creatorChoice == "1":
        question.creator_pref = 1
    else:
        question.creator_pref= 2
    question.save()
    request.session['setting'] = 2
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# poll is open to anonymous voters
def changeType(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    openstring = request.POST['openpoll']
    if openstring == "anon":
        question.open = 1
    elif openstring == "invite":
        question.open = 0
    else:
        question.open = 2
    question.save()
    print(question.open)
    request.session['setting'] = 4
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
# poll is closed to anonymous voters
def closePoll(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.open = 0
    question.save()
    request.session['setting'] = 4
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# poll is closed to anonymous voters, open to people logged in
def uninvitedPoll(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.open = 2
    question.save()
    request.session['setting'] = 4
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def duplicatePoll(request,question_id):
    question = get_object_or_404(Question, pk=question_id)
    title = question.question_text + "_COPY"
    desc = question.question_desc
    voters = question.question_voters.all()
    user = request.user
    items = question.item_set.all()
    new_question = Question(question_text=title, question_desc=desc,
            pub_date=timezone.now(), question_owner=user,
            display_pref=user.userprofile.displayPref, emailInvite=user.userprofile.emailInvite,
            emailDelete=user.userprofile.emailDelete, emailStart=user.userprofile.emailStart,
            emailStop=user.userprofile.emailStop, creator_pref=1)
    new_question.save()
    new_question.question_voters.add(*voters)
    new_items = []
    for item in items:
        new_item = Item(question=new_question,item_text=item.item_text,item_description=item.item_description,timestamp=timezone.now(),image=item.image,imageURL=item.imageURL)
        new_item.save()
        new_items.append(new_item)
    new_question.item_set.add(*new_items)
    setupEmail(new_question)
    return HttpResponseRedirect(reverse('polls:regular_polls'))
    
def deleteUserVotes(request,response_id):
    response = get_object_or_404(Response,pk=response_id)
    user = response.user
    question = response.question
    question.response_set.filter(user=user).update(active=0)
    request.session['setting'] = 6
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def restoreUserVotes(request,response_id):
    response = get_object_or_404(Response,pk=response_id)
    user = response.user
    question = response.question
    question.response_set.filter(user=user,active=0).update(active=1)
    request.session['setting'] = 7
    messages.success(request, 'Your changes have been saved.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# view for ordering voters for allocation
class AllocationOrder(generic.DetailView):
    model = Question
    template_name = 'polls/allocation_order.html' 
    def get_context_data(self, **kwargs):
        ctx = super(AllocationOrder, self).get_context_data(**kwargs)
        currentAllocationOrder = self.object.allocationvoter_set.all()
        tempOrderStr = self.request.GET.get('order', '')
        if tempOrderStr == "null":
            ctx['question_voters'] = self.object.question_voters.all()
            return ctx
        
        # check if the user submitted a vote earlier and display that for modification
        if len(currentAllocationOrder) > 0:
            ctx['currentSelection'] = currentAllocationOrder

        ctx['question_voters'] = self.object.question_voters.all()
        return ctx    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

# manually set the allocation order of voters
def setAllocationOrder(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # get the voter order
    orderStr = request.POST["pref_order"]
    prefOrder = getPrefOrder(orderStr, question)
    if orderStr == "":
        # the user must rank all voters
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  
        
    prefOrder = orderStr.split(",")
    if len(prefOrder) != len(question.question_voters.all()):
        # the user must rank all voters
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

    #reset allocation order
    for voter in question.allocationvoter_set.all():
        voter.delete()

    # find ranking student gave for each item under the question
    item_num = 1
    for item in question.question_voters.all():
        arrayIndex = prefOrder.index("item" + str(item_num))
        if arrayIndex != -1:
            user = question.question_voters.all()[arrayIndex]
            # add pref to list
            voter, created = AllocationVoter.objects.get_or_create(question=question, user=user, response=None)
            voter.save()  

        item_num += 1    
    
    return HttpResponseRedirect(reverse('polls:viewAllocationOrder', args=(question.id,)))

# if the allocation mechanism is early-first or late-first serial dictatorship, assign the order based off of latest response time
# Question question
# List<Response> latest_responses
def getInitialAllocationOrder(question, latest_responses):
    if len(latest_responses) == 0:
        return

    # assign the default allocation order from earliest to latest
    counter = len(question.item_set.all())
    for user_response in (list(reversed(latest_responses))):
        # no more items left to allocate
        if counter == 0:
            return

        counter -= 1
        # create the object
        voter, created = AllocationVoter.objects.get_or_create(question=user_response.question, user=user_response.user)
        # save the most recent response
        voter.response = user_response
        voter.save()     
    return 

# get the current allocation order for this poll
# if this poll is part of a multi-poll, then it must consider the order of the previous subpolls
# Question question
# List<Response> latest_responses
# return Query<AllocationVoter> allocation_order
def getCurrentAllocationOrder(question, latest_responses):
    # get the allocation order from the first multipoll
    allocation_order = []
    if question.m_poll == True:
        multipoll = question.multipoll_set.all()[0]
        firstSubpoll = multipoll.questions.all()[0]
        allocation_order = firstSubpoll.allocationvoter_set.all()
        
        # fix the allocation order from the first subpoll
        if len(allocation_order) == 0:
            # get allocation order
            getInitialAllocationOrder(question, latest_responses)
        else:
            # copy a new allocation order based off of the first subpoll
            for alloc_item in allocation_order:
                voter, created = AllocationVoter.objects.get_or_create(question=question, user=alloc_item.user)
                voter.response = question.response_set.reverse().filter(user=alloc_item.user)[0]
                voter.save()
        allocation_order = question.allocationvoter_set.all()
    else:
        # get the allocation order
        allocation_order = question.allocationvoter_set.all()

        # calculate initial order if there is none or if new voters are added during the poll
        if len(allocation_order) == 0 or len(allocation_order) != len(latest_responses):    
            getInitialAllocationOrder(question, latest_responses)
            allocation_order = question.allocationvoter_set.all()    
    
    return allocation_order

# order user responses similar to the allocation order
# Query<AllocationVoter> allocation_order
# return List<Response>
def getResponseOrder(allocation_order):
    response_set = []
    for order_item in allocation_order:
        question = order_item.question
        user = order_item.user
        
        # skip if no vote
        if question.response_set.reverse().filter(user=user).count() == 0:
            continue        

        # save response
        response = question.response_set.reverse().filter(user=user)[0]
        order_item.response = response
        order_item.save()
        
        # add to the list
        response_set.append(response)
    return response_set

# update the database with the new allocation results
# Question question
# Dict<String, String> allocationResults
def assignAllocation(question, allocationResults):
    for username, item in allocationResults.items():
        currentUser = User.objects.filter(username = username)
        allocatedItem = question.item_set.get(item_text = item)
        mostRecentResponse = question.response_set.reverse().filter(user=currentUser)[0]
        mostRecentResponse.allocation = allocatedItem
        mostRecentResponse.save()
    return

# organize the data into items and responses (most recent) and then apply allocation algorithms 
# to get the final result
# Question question
def getFinalAllocation(question):
    # the latest and previous responses are from latest to earliest
    (latest_responses, previous_responses) = categorizeResponses(question.response_set.filter(active=1).order_by('-timestamp'))

    # no responses, so stop here
    if len(latest_responses) == 0:
        return
    
    allocation_order = getCurrentAllocationOrder(question, latest_responses)
    response_set = getResponseOrder(allocation_order)   # get the list of responses in the specified order 

    # make items and responses generic
    item_set = latest_responses[0].question.item_set.all()
    itemList = []
    for item in item_set:
        itemList.append(item.item_text)          
    responseList = []
    for response in response_set:
        tempDict = {}
        dictionary = {}
        if response.dictionary_set.all().count() > 0:
            dictionary = Dictionary.objects.get(response=response)
        else:
            dictionary = buildResponseDict(response,response.question,getPrefOrder(response.resp_str, response.question))
        for item, rank in dictionary.items():
            tempDict[item.item_text] = rank
        responseList.append((response.user.username, tempDict))
        
    allocationResults = allocation(question.poll_algorithm, itemList, responseList)
    assignAllocation(question, allocationResults)    
    
def calculateCurrentResult(question):

    candMap = getCandidateMapFromList(list(question.item_set.all()))
    indexVoteResults = question.poll_algorithm - 1
    current_result = vote_results[indexVoteResults]
    
    if question.currentresult != None:
        question.currentresult.clear()
    
    result = CurrentResult(question=question,timestamp=pw.response.timestamp,result_string="",mov_string="",cand_num=question.item_set.all().count())
    resultstr = ""
    movstr = ""
    responses = question.response_set.reverse().filter(timestamp__range=[datetime.date(1899, 12, 30), pw.response.timestamp],active=1)
    (lr, pr) = categorizeResponses(responses)
    scorelist, mixtures = getVoteResults(lr,candMap)
    mov = getMarginOfVictory(lr,candMap)
    for x in range(0,len(scorelist)):
        for key,value in scorelist[x].items():
            resultstr += str(value)
            resultstr += ","
    for x in range(0,len(mov)):
        movstr += str(mov[x])
        movstr += ","
    resultstr = resultstr[:-1]
    movstr = movstr[:-1]
    result.result_string = resultstr
    result.mov_string = movstr
    result.save()

            
# function to get preference order from a string 
# String orderStr
# Question question
# return List<List<String>> prefOrder
def getPrefOrder(orderStr, question):
    # empty string
    if orderStr == "":
        return None
    current_array = orderStr.split(";;|;;")
    prefOrder = []
    length = 0
    for item in current_array:
        if item != "":
            curr = item.split(";;")
            prefOrder.append(curr)
            length += len(curr)
    # the user hasn't ranked all the preferences yet
    if length != len(question.item_set.all()):
        return None
    
    return prefOrder

# function to process student submission
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    prevResponseCount = question.response_set.filter(user=request.user).count()
    # get the preference order
    orderStr = request.POST["pref_order"]
    prefOrder = getPrefOrder(orderStr, question)
    if prefOrder == None:
        # the user must rank all preferences
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    # make Response object to store data
    comment = request.POST['comment']
    response = Response(question=question, user=request.user, timestamp=timezone.now(), resp_str = orderStr)
    if comment != "":
        response.comment = comment
    response.save()
    
    #enqueue
    #enqueue(getCurrentResult(question))
    
    #get current winner
    old_winner = OldWinner(question=question, response=response)
    old_winner.save()
    # notify the user that the vote has been saved/updated
    if prevResponseCount == 0:
        messages.success(request, 'Saved!')
    else:
        messages.success(request, 'Updated!')

    if question.open == 2 and request.user not in question.question_voters.all():
        question.question_voters.add(request.user.id)

    return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

# create a new dictionary that stores the preferences and rankings
# Response response
# Question question
# List<List<String>> prefOrder
def buildResponseDict(response, question, prefOrder):
    d = {}

    # find ranking user gave for each item under the question
    item_num = 1
    for item in question.item_set.all():
        rank = 1
        for l in prefOrder:
            string = "item" + str(item)
            if string in l:
                d[item] = rank
                break
            rank += 1
        
        # if arrayIndex == -1:
        #     # set value to lowest possible rank
        #     d[item] = question.item_set.all().count()
        # else:
        #     # add 1 to array index, since rank starts at 1
        #     rank = (prefOrder.index("item" + str(item))) + 1
        #     # add pref to response dict
        #     d[item] = rank
    return d

# join a poll without logging in
def anonymousJoin(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    name = request.POST['name']
    request.session['anonymousvoter'] = name
    return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))
    
# submit a vote without logging in
def anonymousVote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    voter = ""
    id = 0
    # check if the anonymous voter has voted before
    if 'anonymousvoter' not in request.session or 'anonymousid' not in request.session:
        voter = request.POST['anonymousname']
        if voter == "":
            voter = "Anonymous"
        request.session['anonymousvoter'] = voter
        id = question.response_set.all().count()
        request.session['anonymousid'] = id
    else:
        voter = request.session['anonymousvoter']
        id = request.session['anonymousid']
    
    # get the preference order
    orderStr = request.POST["pref_order"]
    prefOrder = getPrefOrder(orderStr, question)
    if prefOrder == None:
        # the user must rank all preferences
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    # make Response object to store data
    comment = request.POST['comment']
    response = Response(question=question, timestamp=timezone.now(), anonymous_voter = voter, anonymous_id=id, resp_str = orderStr)
    if comment != "":
        response.comment = comment
    response.save()

    # find ranking student gave for each item under the question

    #get current winner
    old_winner = OldWinner(question=question, response=response)
    old_winner.save()

    # notify the user that the vote has been updated
    messages.success(request, 'Your preferences have been updated.')
    return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))
    