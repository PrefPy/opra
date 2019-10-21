from .models import *
from appauth.models import *
from groups.models import *
import datetime
import os
import time
import collections

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django import views
from django.db.models import Q

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from prefpy.mechanism import *
from prefpy.allocation_mechanism import *
from prefpy.gmm_mixpl import *
from prefpy.egmm_mixpl import *
from django.conf import settings
from multipolls.models import *

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ApplyForm

import json
import threading
import itertools
import numpy as np
import random
import csv
import logging

class IndexView(views.generic.ListView):
    """
        Define homepage view, inheriting ListView class, which specifies a context variable.
        
        Note that login is required to view the items on the page.
        """
    
    template_name = 'mentors/index.html'
    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)

        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        return ctx

    def get_queryset(self):
        """Override function in parent class and return all questions."""
        
        return Mentor.objects.all()

class ApplyView(views.generic.ListView):
    template_name = 'mentors/apply.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        
        if (Mentor.applied):
            ctx['step'] = Mentor.step
        else:
            ctx['step'] = 1
            Mentor.step = 1

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

class view_applyView(views.generic.ListView):
    template_name = 'mentors/view_application.html'
    def get_context_data(self, **kwargs):
        ctx = super(view_applyView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# view of personal infomation page
class ApplyPersonalInfoView(views.generic.ListView):
    template_name = 'mentors/apply_personal_info.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyPersonalInfoView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# view of compensation and reponsibility page
class ApplyCompensationView(views.generic.ListView):
    template_name = 'mentors/apply_compensation.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyCompensationView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        ctx['step'] = Mentor.step

        return ctx

    def get_queryset(self):
        return Mentor.objects.all()

# view of preference of a student applicant page
class ApplyPreferenceView(views.generic.ListView):
    template_name = 'mentors/apply_preference.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyPreferenceView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        ctx['step'] = Mentor.step

        # === need more for course data ===

        return ctx

    def get_queryset(self):
        return Mentor.objects.all()


def applystart(request):
    new_applica = Mentor()

# apply step
def applystep(request):
    if request.method == 'POST':
        # initate a new mentor applicant
        if ( Mentor.step == 1):
            new_applicant = Mentor()
            new_applicant.RIN = request.POST['rin']
            new_applicant.first_name = request.POST['fname']
            new_applicant.last_name = request.POST['lname']
            new_applicant.GPA = request.POST['gpa']
            new_applicant.phone = request.POST['phone']
            new_applicant.RPI_email = request.POST['email']
            new_applicant.recommender = request.POST['recommender']

            new_applicant.save()
        
        #Mentor.applied = True
        Mentor.step += 1
   
    return render(request, 'mentors/apply.html', {'step': Mentor.step})

# withdraw application, should add semester later
def withdraw(request):
    if request.method == 'GET':

        Mentor.objects.all().delete()
        Mentor.applied = False
    return HttpResponseRedirect(reverse('mentors:index'))