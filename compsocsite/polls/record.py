import datetime
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.urlresolvers import reverse
from django.views import generic
from django.core.files import File
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

def writeUserAction(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        #session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        #str = "/log/" + request.user.username + "_" + session_key + ".txt"
        #f = open(str, 'w+')
        data = request.POST['data']
        #print(data)
        r = UserVoteRecord(timestamp=timezone.now(),user=request.user,record=data,question=question)
        r.save()
        #f.close()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def interpretRecord(record):
    r = record.record
    action_arr = r.split(";;")
    record_arr = []
    temp = []
    temp.append(record.user.username)
    temp.append(str(record.timestamp))
    record_arr.append(temp)
    for str1 in action_arr:
        t = str1.split("::")
        if len(t) == 4:
            t[2] = t[2][4:]
            record_arr.append(t)
    return record_arr
    
class RecordView(generic.DetailView):
    model = Question
    template_name = 'polls/record.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(RecordView, self).get_context_data(**kwargs)
        records = self.object.uservoterecord_set.all()
        interpreted_records = []
        for r in records:
            interpreted_records.append(interpretRecord(r))
        ctx['user_records'] = interpreted_records
        return ctx