from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
    	"""
    	Return the last five published questions (not including those set to be published in the future).
    	"""
    	return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

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

def vote(request, question_id):
    # return HttpResponse("You're voting on question %s." % question_id)
    # TODO:
    # make Response with student's name, current time, question
    # go through each item and identify which radio button has been selected
    # add item + radio button ranking to Response's Dictionary
    # if no button selected on a given item, set to highest possible selection
    # HttpResponseRedirect to thank you screen
    question = get_object_or_404(Question, pk=question_id)
    response = Response(question=question, student=Student.objects.get(student_name=request.POST['Name']), timestamp=timezone.now())
    response.save()
    d = response.dictionary_set.create(name = response.student.student_name + " Preferences")

    item_num = 0
    for item in question.item_set.all():
        try:
            selected_choice = item.get(pk=request.POST['item'+str(item_num)])
        except:
            # set value to lowest possible rank
            d[item] = question.item_set.all().count()
        else:
            # add pref to response dict
            d[item] = int(selected_choice.value)
        d.save()
        item_num += 1
    return HttpResponseRedirect(reverse('polls:index'))


# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))