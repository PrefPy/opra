import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

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
		
	return HttpResponse("Your question: " + questionString)
  
    return render_to_response('polls/add.html', {}, context)    

# view for question detail
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)
        ctx['students'] = Student.objects.all()
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


