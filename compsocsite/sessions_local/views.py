from django.shortcuts import render
import datetime
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django import views
from polls import opra_crypto
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils import timezone
from django.core.urlresolvers import reverse
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
        ctx['sessions_manageable'] = self.request.user.session_set.all().order_by('-pub_date')
        ctx['sessions_participated'] = self.request.user.sessions_participated.order_by('-pub_date')
        return ctx
        
class SessionView(views.generic.DetailView):
    model = Session
    template_name = "session_detail.html"
    def get_context_data(self, **kwargs):
        ctx = super(SessionView, self).get_context_data(**kwargs)
        ctx['participants'] = self.object.participants.all()
        ctx['admins'] = self.object.admins.all()
        return ctx
        
@login_required
def createSession(request):
    context = RequestContext(request)
    if request.method == "POST":
        session_title = request.POST["title"]
        session_description = request.POST["description"]
        session = Session(title=session_title, description=session_description,pub_date=timezone.now(),creator=request.user)
        session.save()
        link = "https://opra.cs.rpi.edu/sessions/join/" +  opra_crypto.encrypt(session.id) +"/"
        session.link = link
        session.save()
        return HttpResponseRedirect(reverse("sessions_local:sessions_main"))
    return render(request, 'create_session.html', {})
    
@login_required
def joinSession(request,key):
    context = RequestContext(request)
    id = opra_crypto.decrypt(key)
    session = get_object_or_404(Session, pk=id)
    if request.user not in session.participants.all():
        session.participants.add(request.user.id)
    return render(request, 'success.html', {})