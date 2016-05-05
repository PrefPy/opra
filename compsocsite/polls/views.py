import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_list'

    def get_queryset(self):
    	return Question.objects.all().order_by('-pub_date')

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

# TODO: change this
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

class ConfirmationView(generic.DetailView):
    model = Question
    template_name = 'polls/confirmation.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    response = Response(question=question, student=Student.objects.get(student_name=request.POST['name']), timestamp=timezone.now())
    response.save()
    d = response.dictionary_set.create(name = response.student.student_name + " Preferences")

    item_num = 1
    for item in question.item_set.all():
        try:
            selected_choice = request.POST["item" + str(item_num)]
        except:
            # set value to lowest possible rank
            print "The .POST is not working sadly."
            d[item] = question.item_set.all().count()
        else:
            # add pref to response dict
            d[item] = int(selected_choice)
        d.save()
        item_num += 1
    return HttpResponseRedirect(reverse('polls:confirmation', args=(question.id,)))

