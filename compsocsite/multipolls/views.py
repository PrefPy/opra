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
from polls.views import getPollWinner
# Create your views here.


def AddStep1(request):
    context = RequestContext(request)
    if request.method == 'POST':
        number1 = request.POST['n']
        number = int(number1)
        title = request.POST['mPollTitle']
        description = request.POST['desc']
        questionType = request.POST['questiontype']
        multipoll = MultiPoll(number=number, pos=0, status=0, title=title, description=description, owner=request.user)
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
    return render_to_response('multipolls/add_step1.html', {}, context)
    
class AddStep2View(generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/add_step2.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep2View, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
        
class AddStep3View(generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/add_step3.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep3View, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
        
class AddStep4View(generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/add_step4.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddStep4View, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        ctx['preference'] = self.request.user.userprofile.displayPref
        ctx['poll_algorithms'] = ["Plurality", "Borda", "Veto", "K-approval (k = 3)", "Simplified Bucklin", "Copeland", "Maximin"]
        ctx['view_preferences'] = ["Everyone can see all votes", "Only show the names of voters", "Only show number of voters", "Everyone can only see his/her own vote"]
        return ctx
        
class SetVotersView(generic.DetailView):
    model = MultiPoll
    template_name = 'multipolls/setvoters.html'
    def get_context_data(self, **kwargs):
        ctx = super(SetVotersView, self).get_context_data(**kwargs)
        ctx['question'] = self.get_object().questions.all()[self.get_object().pos]
        ctx['users'] = User.objects.all()
        ctx['items'] = Item.objects.all()
        ctx['groups'] = Group.objects.all()
        return ctx
        


def setQuestion(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll, pk=multipoll_id)
    questionString = request.POST['questionTitle']   
    questionDesc = request.POST['desc']
    imageURL = request.POST['image']
    question = multipoll.questions.all()[multipoll.pos]
    question.question_text = questionString
    question.question_desc = questionDesc
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
        print("qwe")
        return HttpResponseRedirect('/multipolls/%s/setvoters' % multipoll.id)
    else:
        multipoll.pos += 1
        multipoll.save()
        print("asd")
        return HttpResponseRedirect('/multipolls/%s/add_step2' % multipoll.id)

def removeVoter(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    newVoters = request.POST.getlist('voters')
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        multipoll.voters.remove(voterObj.id)
        for question in multipoll.questions:
            question.question_voters.remove(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def addVoter(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)

    newVoters = request.POST.getlist('voters')
    for voter in newVoters:
        voterObj = User.objects.get(username=voter)
        multipoll.voters.add(voterObj.id)
        for question in multipoll.questions:
            question.question_voters.add(voterObj.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def start(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    multipoll.status = 1
    for question in multipoll.questions.all():
        question.status = 2
        question.save()
    multipoll.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def progress(request, multipoll_id):
    multipoll = get_object_or_404(MultiPoll,pk=multipoll_id)
    #poll hasn't started
    if multipoll.status < multipoll.number:
        question = multipoll.questions.all()[multipoll.status-1]
        #end the previous poll   
        question.status = 3
        if question.question_type == 1: #poll
            question.winner = getPollWinner(question)
        elif question.question_type == 2: #allocation
            allocation_serial_dictatorship(question.response_set.all())
        question.save()
        #move to the next poll
        multipoll.status += 1
        multipoll.save()
        #This part is for checking conditional preferences
        poll = multipoll.questions.all()[multipoll.status-1]
        for combination in poll.combination_set.all():
            flag = True
            for item in combination.dependencies.all():
                if item.item_text not in item.question.winner:
                    flag = False
            if flag == True:
                response = combination.response
                response.question = poll
                response.save()
    #all the polls have ended
    else:
        #end the last poll
        question = multipoll.questions.all()[multipoll.status-1]
        question.status = 3
        if question.question_type == 1: #poll
            question.winner = getPollWinner(question)
        elif question.question_type == 2: #allocation
            allocation_serial_dictatorship(question.response_set.all())
        question.save()
        multipoll.status += 1
        multipoll.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        