from django.shortcuts import render
import datetime
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django import views
from polls import opra_crypto
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
# Create your views here.


class SessionsMainView(views.generic.ListView):
    template_name = 'sessions_main.html'
    context_object_name = 'session_list'
    def get_queryset(self):
        return Session.objects.all()
    def get_context_data(self, **kwargs):
        ctx = super(SessionsMainView, self).get_context_data(**kwargs)
        # sort the lists by date (most recent should be at the top)
        ctx['sessions_created'] = Session.objects.filter(creator=self.request.user).order_by('-pub_date')
        ctx['sessions_manageable'] = Session.objects.filter(admins__contains=self.request.user).order_by('-pub_date')
        ctx['sessions_participated'] = self.request.user.sessions_participated.exclude(creator=self.request.user,admins__contains=self.request.user).order_by('-pub_date')
        return ctx
        
class SessionView(views.generic.DetailView):
    model = Session
    template_name = "session.html"
    def get_context_data(self, **kwargs):
        ctx = super(SessionView, self).get_context_data(**kwargs)
        ctx['participants'] = self.object.participants.all()
        ctx['admins'] = self.object.admins.all()
        return ctx
        
def createSession(request):
    if request.method == "POST":
        session_title = request.POST["title"]
        session_description = request.POST["description"]
        session = Session(title=session_title, description=session_description,pub_date=timezone.now(),creator=request.user)
        print(session.id)
        link = "https://opra.cs.rpi.edu/sessions/join/" +  opra_crypto.encrypt(session.id) +"/"
        session.link = link
        session.save()
    return HttpResponseRedirect(reverse("sessions:sessions_main"))
    
def joinSession(request,key):
    id = opra_crypto.decrypt(key)
    session = get_object_or_404(Session, pk=id)