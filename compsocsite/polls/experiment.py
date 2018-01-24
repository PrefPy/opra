import datetime
import os
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.urlresolvers import reverse
from django import views

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from prefpy.mechanism import *
from groups.models import *
from django.conf import settings
import random
import string
import threading

def createNewExperiment(request):
    if request.method == 'POST':
        title_text = request.POST["title"]
        exp = Experiment(title=title_text,timestamp=timezone.now())
        exp.save()
        return HttpResponseRedirect(reverse('polls:',args=(exp.id,)))
    return render(request,'events/Mturk/AddExperiment.html',{})

class ExperimentSetup(views.generic.DetailView):
    model = Experiment
    template_name = 'events/Mturk/ExperimentDetail.html'

    def get_context_data(self, **kwargs):
        ctx = super(ExperimentSetup, self).get_context_data(**kwargs)
        return ctx

def addPollToExperiment(request, exp_id):
    if request.method == 'POST':
        poll_id = request.POST['poll_id']
        try:
            poll_id_int = int(poll_id)
            exist = Question.objects.filter(id=poll_id_int).exists()
            if not exist:
                return HttpResponse("Poll does not exist!")
            exp = get_object_or_404(Experiment, pk=exp_id)
            polls = json.loads(exp.polls)
            if poll_id_int not in polls:
                polls.append(poll_id_int)
                polls_str = json.dumps(polls)
                exp.polls = polls_str
                exp.save()
        except ValueError:
            return HttpResponse("The value you entered is not valid!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))