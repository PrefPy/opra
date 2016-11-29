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
        order = request.POST['order']
        device = request.POST['device']
        #print(data)
        if request.user.username == "":
            anonymous_name = ""
            new_name = "(Anonymous)" + anonymous_name
            r = UserVoteRecord(timestamp=timezone.now(),user=new_name,record=data,question=question,initial_order=order,device=device)
            r.save()
        else:
            r = UserVoteRecord(timestamp=timezone.now(),user=request.user.username,record=data,question=question,initial_order=order,device=device)
            r.save()
        #f.close()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def interpretRecord(record):
    order = record.initial_order
    order_arr = order.split(";;")
    order = ""
    for i in order_arr:
        order += i[4:] + "; "
    r = record.record
    action_arr = r.split(";;;")
    record_arr = []
    temp = ""
    temp += record.user + " voted at " + str(record.timestamp) + "\n"
    if order != "":
        temp += "\nInitial order: " + order
    record_arr.append(temp)
    record_arr.append(record.device)
    for str1 in action_arr:
        if str1.find(";;") != -1:
            pair = str1.split(";;")
            if len(pair) == 2:
                t1 = pair[0].split("::")
                t2 = pair[1].split("::")
                t1[2] = t1[2][4:]
                t2[2] = t2[2][4:]
                if t1[1] == "start":
                    str2 = ""
                    item_arr = t2[3].split("||")
                    str2 += "Moved item " + t1[2] + " from tier " + t1[3] + " to tier " + item_arr[0] + " at time " + t1[0] + ", tier " + item_arr[0] + " has items: "
                    for index in range(1,len(item_arr)):
                        if(item_arr[index] != ""):
                            str2 += item_arr[index][4:] + ", "
                    record_arr.append(str2)
                else:
                    str2 = ""
                    str2 += "Clicked item " + t1[2] + " on the right at tier " +t1[3] + " and moved it to tier " + t2[3] + " on the left at time " + t1[0] + "."
                    record_arr.append(str2)
        else:
            if len(str1) != 0:
                if str1.find("||") == -1:
                    str2 = "Clicked move all at time " + str1 + "."
                    record_arr.append(str2)
                else:
                    clear_arr = str1.split("||")
                    str2 = "Clicked clear at time " + clear_arr[0] + ", order on the right is: "
                    for i in range(1,len(clear_arr)):
                        str2 += clear_arr[i][4:] + "; "
                    record_arr.append(str2)
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