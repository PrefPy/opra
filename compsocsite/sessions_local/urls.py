from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'sessions_local'
urlpatterns = [
    #Two main types of polls
    url(r'^$', login_required(views.SessionsMainView.as_view()), name='sessions_main'),
    url(r'^(?P<pk>[0-9]+)/$', views.SessionView.as_view(), name='info'),
    url(r'^createsession/$', views.createSession, name='create_session'), 
]