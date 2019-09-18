from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from polls.views import getPollWinner
from prefpy.allocation_mechanism import *
from polls.views import *

from itertools import *

def AddStep1(request):
    context = RequestContext(request)
    if request.method == 'POST':
        number1 = request.POST['n']
        number = int(number1)
        title = request.POST['mPollTitle']
        description = request.POST['desc']
        questionType = request.POST['questiontype']
        multipoll = MultiPoll(number=number, pos=0, status=0, title=title, description=description, owner=request.user)
        multipoll.emailInvite = request.user.userprofile.emailInvite
        multipoll.emailDelete = request.user.userprofile.emailDelete        
        multipoll.save()
        for x in range(0, number):
            question = Question(question_text="Multipoll Issue", question_desc="",
                    image="", pub_date=timezone.now(), question_owner=request.user,
                    display_pref=request.user.userprofile.displayPref, m_poll=True)
            question.question_type = questionType
            question.save()
            m = MultiPollQuestion(multipoll=multipoll,question=question,order=x)
            m.save()
        multipoll.save()
        return HttpResponseRedirect('/multipolls/%s/add_step2' % multipoll.id)
    return render(request,'multipolls/add_step1.html', {})
    
class AddStep2View(views.generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/add_step2.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep2View, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        return ctx
        
class AddStep3View(views.generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/add_step3.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep3View, self).get_context_data(**kwargs)
        question = self.get_object().questions.all()[self.get_object().pos]
        ctx['question'] = question
        ctx['items'] = question.item_set.all()
        ctx['preference'] = self.request.user.userprofile.displayPref
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = getAllocMethods()
        ctx['view_preferences'] = getViewPreferences()    
        return ctx
        
class SetVotersView(views.generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/setvoters.html'
    def get_context_data(self, **kwargs):
        ctx = super(SetVotersView, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        ctx['users'] = User.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx

def setQuestion(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id)
    questionString = request.POST['questionTitle']   
    questionDesc = request.POST['desc']
    imageURL = request.POST['imageURL']
    
    question = multipoll.questions.all()[multipoll.pos]
    question.question_text = questionString
    question.question_desc = questionDesc
    if request.FILES.get('docfile') != None:
        question.image = request.FILES.get('docfile')    
    if imageURL != '':
        question.imageURL = imageURL
    question.save()
    return HttpResponseRedirect('/multipolls/%s/add_step3' % multipoll_id)
 
def setInitialSettings(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id)
    question = multipoll.questions.all()[multipoll.pos]
    question.poll_algorithm = request.POST['pollpreferences']
    question.display_pref = request.POST['viewpreferences']
    question.save()
    temp = multipoll.number - 1
    if multipoll.pos == temp:
        multipoll.pos = 0
        multipoll.save()
        return HttpResponseRedirect('/multipolls/%s/setvoters' % multipoll.id)
    else:
        multipoll.pos += 1
        multipoll.save()
        return HttpResponseRedirect('/multipolls/%s/add_step2' % multipoll.id)

# remove a single voter from all subpolls
def removeVoter(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id)
    email = request.POST.get('email') == 'email'
    multipoll.emailDelete = email
    multipoll.save()    
    newVoters = request.POST.getlist('voters')
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        multipoll.voters.remove(voterObj.id)
        for question in multipoll.questions.all():
            question.question_voters.remove(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
# add a single voter to all subpolls
def addVoter(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    email = request.POST.get('email') == 'email'
    multipoll.emailInvite = email  
    multipoll.save()
    newVoters = request.POST.getlist('voters')
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        multipoll.voters.add(voterObj.id)
        for question in multipoll.questions.all():
            question.question_voters.add(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# add everyone in the group to all subpolls
def addGroupVoters(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    email = request.POST.get('email') == 'email'
    multipoll.emailInvite = email  
    multipoll.save()    
    newGroups = request.POST.getlist('groups')
    for group in newGroups:
        for cur in Group.objects.all():
            if cur.owner == request.user and cur.name == group:
                groupObj = cur
                for voter in groupObj.members.all():
                    if voter not in multipoll.voters.all():
                        voterObj = User.objects.get(username=voter)
                        multipoll.voters.add(voterObj.id)
                        for question in multipoll.questions.all():
                            question.question_voters.add(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# remove everyone in the group from all multipoll
def removeGroupVoters(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    newGroups = request.POST.getlist('groups')
    for group in newGroups:
        for cur in Group.objects.all():
            if cur.owner == request.user and cur.name == group:
                groupObj = cur
                for voter in groupObj.members.all():
                    if voter in multipoll.voters.all():
                        voterObj = User.objects.get(username=voter)
                        multipoll.voters.remove(voterObj.id)
                        for question in multipoll.questions.all():
                            question.question_voters.remove(voterObj.id)                    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# start all subpolls in the multipoll
def start(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    
    # start the multipoll
    multipoll.status = 1
    
    # start all subpolls
    for question in multipoll.questions.all():
        question.status = 2
        question.save()
    multipoll.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# end the current subpoll in the sequence
# MultiPoll multipoll
def endSubpoll(multipoll):
    #end the previous poll
    question = multipoll.questions.all()[multipoll.status - 1]
    question.status = 3
    
    # get results for this subpoll
    if question.question_type == 1: #poll
        question.winner = getPollWinner(question)[0]
    elif question.question_type == 2: #allocation
        getFinalAllocation(question)
    question.save()
    
    #move to the next poll
    multipoll.status += 1
    multipoll.save()    

# end the next poll in the sequence    
def progress(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id) 
    endSubpoll(multipoll)

    #poll in session
    if multipoll.status < multipoll.number:        
        # check conditional preferences
        poll = multipoll.questions.all()[multipoll.status-1]
        for combination in poll.combination_set.all(): 
            for condition in combination.conditionalitem_set.all(): 
                flag = True
                for item in condition.items.all():
                    if poll.question_type == 1: # poll
                        # this combination does not have the winner
                        if item.item_text not in item.question.winner:
                            flag = False
                    elif poll.question_type == 2:
                        user = request.user
                        latest_response = item.question.response_set.all().filter(user=user)[0]
                        # this combination does not have the allocation
                        if latest_response.allocation != item:
                            flag = False                        

                # save this response
                if flag == True:
                    response = condition.response
                    if response != None:
                        response.question = poll
                        response.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class mpollinfoView(views.generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/mpollinfo.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(mpollinfoView, self).get_context_data(**kwargs)
        mpoll=self.get_object()
    
        latest_responses=[]
        previous_responses=[]
        mostRecentResponse=[]
        history=[]

        for question in self.get_object().questions.all():
            tmp_lr={}
            tmp_pr={}
            tmp_lr['id']= question.id
            tmp_pr['id']=question.id
            all_responses = question.response_set.reverse()
            (lr1, pr1) = categorizeResponses(all_responses)
            tmp_lr['main']= lr1
            tmp_pr['main']= pr1
            latest_responses.append(tmp_lr)
            previous_responses.append(tmp_pr)
            
            tmp_mrr={}
            tmp_history={}
            tmp_mrr['id']=question.id
            tmp_history['id']=question.id
            currentUserResponses = question.response_set.filter(user=self.request.user).reverse()
            tmp_mrr['main']=currentUserResponses[0] if (len(currentUserResponses) > 0) else None
            tmp_history['main']=currentUserResponses[1:]
            mostRecentResponse.append(tmp_mrr)
            history.append(tmp_history)

        ctx['mpoll']= mpoll
        ctx['users'] = User.objects.all()
        ctx['groups'] = Group.objects.all()
        ctx['poll_algorithms'] = getListPollAlgorithms()
        ctx['alloc_methods'] = getAllocMethods()  

        ctx['lr'] = latest_responses
        ctx['pr'] = previous_responses
        
        ctx['mrr'] = mostRecentResponse
        ctx['hist'] = history
    
        return ctx
    
def deleteMpoll(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id)
    # check to make sure the current user is the owner
    if request.user != multipoll.owner:
        # quit
        for question in multipoll.questions.all():
            question.question_voters.remove(request.user)
            question.save()
        multipoll.voters.remove(request.user)
        return HttpResponseRedirect(reverse('polls:m_polls'))  
    else:
        # delete
        for question in multipoll.questions.all():
            question.delete()
        multipoll.delete()
        
        return HttpResponseRedirect(reverse('polls:m_polls'))
    
# edit title and description
def editBasicInfo(request, multipoll_id):
    question = get_object_or_404(MultiPoll, pk=multipoll_id)
    new_title = request.POST["Mtitle"]
    new_desc = request.POST["Mdesc"]    
    question.title = new_title
    question.description = new_desc    
    question.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   

# display the dependent polls selected 
# allow the user to vote on this poll given the preferences for the previous dependent polls
class DependencyView(views.generic.DetailView):
    model = Question
    template_name = 'multipolls/dependency.html'
    def get_order(self, ctx):
        otherUserResponses = self.object.response_set.reverse()
        defaultOrder = self.object.item_set.all()
        return defaultOrder
        #commented out to improve performance
        #return getRecommendedOrder(otherUserResponses, self.request, defaultOrder)    

    def get_context_data(self,**kwargs):
        ctx = super(DependencyView, self).get_context_data(**kwargs) 
        
        # use a single combination object
        combination, created = Combination.objects.get_or_create(target_question=self.object, user=self.request.user)
        combination.save()        
        ctx['combination'] = combination      
        
        # get the pref graph for display
        (nodes, edges) = getPrefenceGraph(self.request, self.object)
        ctx['pref_nodes'] = nodes
        ctx['pref_edges'] = edges
        
        # get the current poll
        ctx['question'] = combination.target_question

        # get the prev and next polls
        currentIndex = self.object.multipollquestion_set.all()[0].order
        multipoll = self.object.multipoll_set.all()[0]
        ctx['prev_poll'] = multipoll.questions.all()[currentIndex - 1] if currentIndex > 0 else None
        ctx['next_poll'] = multipoll.questions.all()[currentIndex + 1] if currentIndex < multipoll.questions.count() - 1 else None

        # calculate condition index based off of the current session
        conditionsSelected = [] 
        for poll in combination.dependent_questions.all():
            # no options for this poll
            if poll.item_set.count() == 0:
                continue
            
            # default option is selected
            if "set_default" in self.request.session and self.request.session["set_default"] == True:
                break

            option = getSelectedItem(self.request.session, poll)
            conditionsSelected.append(option)
        conditionIndex = getConditionIndex(conditionsSelected, combination)

        # if the user has responded to this question, then load the response
        conditionalSet = combination.conditionalitem_set.all()
        ctx["colorArray"] = getConditionColor(combination)

        # get the default preferences if there are any
        defaultResponse = getConditionFromResponse([], combination).response        
    
        # check if the condition already exists
        if len(conditionalSet) > 0 and conditionIndex > -1 and conditionIndex < len(conditionalSet) and conditionalSet[conditionIndex].response != None:
            selectedCondition = conditionalSet[conditionIndex]
            condition_items = list(selectedCondition.items.all())
            ctx["condition_items"] = condition_items
            ctx["condition_responses"] = getCurrentSelection(selectedCondition.response)  
        else:
            # this combination of choices does not have a response
            # mark these choices as selected instead of the default ones
            pollChoiceDict = {}
            for poll in combination.dependent_questions.all():
                # no options for this poll
                if poll.item_set.count() == 0:
                    continue

                pollStr = "poll" + str(poll.id)
                pollChoiceDict[pollStr] = getSelectedItem(self.request.session, poll)
            ctx["poll_choice_dict"] = pollChoiceDict

        if defaultResponse != None:
            ctx["default_response"] = getCurrentSelection(defaultResponse)        
        ctx['items'] = self.get_order(ctx)        
        return ctx

# get the item that is currently selected for each subpoll
# request.session session
# Question poll
# return Item option
def getSelectedItem(session, poll):
    pollStr = "poll" + str(poll.id)
    
    # check if there is a session in progress
    if pollStr in session:
        selectedChoice = session[pollStr]

        if selectedChoice == 'null':
            # default: use the first option in the list
            option = poll.item_set.all()[0]
        elif ',' in selectedChoice:
            # if multiple options were selected, pick the first one
            option = poll.item_set.get(item_text = selectedChoice.split(',')[0])
        else:
            # use the variable from the current session
            option = poll.item_set.get(item_text = selectedChoice)
    else:
        # default: use the first option in the list
        option = poll.item_set.all()[0]    
    
    return option

# color the conditions so that you know which conditions have preferences submitted
# Combination combination
# return List<List<String>> colorsArray
def getConditionColor(combination):
    colorsArray = []
    greenColor = "#3CB371"
    yellowColor = "#F0F090"
    redColor = "#FA8072"    

    conditionalSet = combination.conditionalitem_set.all()

    subpollChoicesList = []
    for poll in combination.dependent_questions.all():
        itemList = list(poll.item_set.all())           
        subpollChoicesList.append(itemList)
    totalOptions = len(list(itertools.product(*subpollChoicesList)))
    
    # iterate through all the polls
    for poll in combination.dependent_questions.all():
        colorRow = []
        # iterate through all the choices in a poll
        for item in poll.item_set.all():
            found = False
            # check if that choice has been used in a conditional preference
            counter = 0
            for condition in conditionalSet:
                if item in condition.items.all():
                    counter += 1
                    found = True

            totalForOption = totalOptions / len(poll.item_set.all())
            if found == True:
                # partially filled
                if counter < totalForOption:
                    colorRow.append(yellowColor)
                else: # completely filled 
                    colorRow.append(greenColor)
            else:
                # none
                colorRow.append(redColor)
        colorsArray.append(colorRow)
    return colorsArray

# choose a dependent poll
def chooseDependency(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # get the polls selected
    dependencies = []
    l = request.POST.getlist('polls')
    for poll in l:
        i = int(poll)
        dependencies.append(poll)

    # use a single combination object
    combination, created = Combination.objects.get_or_create(target_question=question, user=request.user)
    if created == False:
        combination.dependent_questions.clear()
    combination.save()
 
    # save a list of dependent questions 
    if len(dependencies) > 0:
        for poll in dependencies:
            combination.dependent_questions.add(poll)
            combination.save()
    return HttpResponseRedirect(reverse('polls:dependencyview', args=(combination.target_question.id,)))

# take previous polls into account as well as the current poll    
def assignPreference(request, combination_id):
    combination = get_object_or_404(Combination, pk=combination_id)
    question = get_object_or_404(Question, pk=combination.target_question.id)

    # get the preference order for this particular combination
    orderStr = request.POST["pref_order"]
    print(orderStr)
    prefOrder = getPrefOrder(orderStr, question)
    if prefOrder == None:
        # the user must rank all preferences
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))    

    # make Response object to store data
    response = Response(question=question, user=request.user, timestamp=timezone.now(),resp_str = orderStr)
    response.save()

    # submit conditional preferences 
    if "default_pref" not in request.POST:  
        # for each depedent poll, get the choice selected
 
        # get all the choices selected for each poll
        subpollChoicesList = []
        for poll in combination.dependent_questions.all():
            s = str(poll.id)
            if s not in request.POST:
                continue
            itemList = request.POST.getlist(s)
            subpollChoicesList.append(itemList)

        # iterate through all possible conditions
        for tupleChoices in itertools.product(*subpollChoicesList):
            listChoices = list(tupleChoices)
            
            # get the conditions selected
            index = 0
            conditionsSelected = []
            for choice in listChoices:
                poll = combination.dependent_questions.all()[index]
                item = poll.item_set.get(item_text = choice)
                conditionsSelected.append(item)
                index += 1
            
            # check if a response has been submitted for this condition    
            condition = getConditionFromResponse(conditionsSelected, combination)
            condition.response = response
            condition.save()

    # update response dictionary
    #buildResponseDict(response, question, prefOrder)    

    # set default pref
    if "default_pref" in request.POST:
        allConditions = ConditionalItem.objects.filter(combination=combination)
        defaultCondition = None
        for currentCondition in allConditions:
            if len(list(currentCondition.items.all())) == 0:
                defaultCondition = currentCondition
                break
        if defaultCondition == None:
            defaultCondition = ConditionalItem(combination=combination)
            defaultCondition.save()
        
        defaultCondition.response = response
        defaultCondition.save()
    
    # notify the user that the vote has been updated
    messages.success(request, 'Updated!')
        
    return HttpResponseRedirect(reverse('multipolls:dependencyview', args=(combination.target_question.id,)))

# build a preference graph given the question dependencies
# request request
# Question question
# return (List<Dict> nodes, List<Dict> edges)
def getPrefenceGraph(request, question):
    multipoll = question.multipoll_set.all()[0] 
    # get the nodes
    nodes = []
    for poll in multipoll.questions.all():
        data = {}
        data['id'] = poll.id
        data['label'] = poll.question_text
        nodes.append(data)    
    # get the edges
    edges = []
    for poll in multipoll.questions.all():
        currentCombination = Combination.objects.filter(target_question=poll, user=request.user)
        if len(currentCombination) > 0:
            dependentPolls = currentCombination[0].dependent_questions.all()

            for dep_poll in dependentPolls:
                data = {}
                data['from'] = dep_poll.id
                data['to'] = poll.id
                data['value'] = 1
                edges.append(data)   
    return (nodes, edges)

# redraw the dependency graph
def updatePrefGraph(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # get the combination object
    combinations = Combination.objects.filter(target_question=question, user=request.user)
    if len(combinations) > 0:
        combination = combinations[0]
        combination.dependent_questions.clear()
    else:
        combination = Combination(target_question=question, user=request.user)
        combination.save()
        
    # get polls selected
    pollsSelected = []  
    for poll in question.multipoll_set.all()[0].questions.all():
        pollStr = "poll" + str(poll.id)
        if pollStr in request.GET:
            if request.GET[pollStr] == "true":
                combination.dependent_questions.add(poll.id)

    return HttpResponseRedirect(reverse('multipolls:dependencyview', args=(question.id,)))

# check if there is a response for this set of conditions and return the condition object
# create a new one if there is no existing objects
# List<Item> conditionsSelected
# Combination combination
# return Condition condition
def getConditionFromResponse(conditionsSelected, combination):
    # check if a response has been submitted for this condition    
    allConditions = ConditionalItem.objects.filter(combination=combination)
    for currentCondition in allConditions:
        # the list of conditions is equal
        if list(currentCondition.items.all()) == conditionsSelected:
            return currentCondition

    # create a new condition object
    condition = ConditionalItem(combination=combination)
    condition.save()
    for item in conditionsSelected:
        condition.items.add(item)
    condition.save()
    return condition

# find the index in the array
# List<Item> conditionsSelected
# Combination combination
# return int conditionIndex
def getConditionIndex(conditionsSelected, combination):
    # check if a response has been submitted for this condition    
    allConditions = ConditionalItem.objects.filter(combination=combination)
    conditionIndex = 0
    for currentCondition in allConditions:
        if list(currentCondition.items.all()) == conditionsSelected:
            return conditionIndex
        conditionIndex += 1
    
    # not found
    return -1
    
# preload the response based off of the condition(s) selected
def getConditionalResponse(request, combination_id):
    combination = get_object_or_404(Combination, pk=combination_id)
    
    # save the poll responses
    for poll in combination.dependent_questions.all():
        pollStr = "poll" + str(poll.id)
        if pollStr in request.GET:
            request.session[pollStr] = request.GET[pollStr]

    if "set_default" in request.GET:
        request.session["set_default"] = True
    else:
        request.session["set_default"] = False

    # set a parameter to the condition index, so that the response to that conditon will be preloaded
    return HttpResponseRedirect(reverse('multipolls:dependencyview', args=(combination.target_question.id,)))