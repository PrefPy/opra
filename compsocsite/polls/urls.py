from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.addView, name='add'),  
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<question_id>[0-9]+)/choice/add/$', views.addChoice, name='addchoice'),
    url(r'^choice/delete/([0-9]+)/$', views.deleteChoice, name='delchoice'),
    url(r'^delete/([0-9]+)/$', views.deletePoll, name='delpoll'),
    url(r'^(?P<question_id>[0-9]+)/addvoter/$', views.addVoter, name='addvoter'),
    url(r'^(?P<question_id>[0-9]+)/delvoter/$', views.removeVoter, name='delvoter'),
    url(r'^(?P<pk>[0-9]+)/settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^(?P<question_id>[0-9]+)/start/$', views.startPoll, name='start'),  
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<question_id>[0-9]+)/stop/$', views.stopPoll, name='stop'),
    url(r'^(?P<question_id>[0-9]+)/setview/$', views.setview, name='setview'),
    url(r'^(?P<pk>[0-9]+)/vote/results/$', views.VoteResultsView.as_view(), name='voteresults'),
    url(r'^(?P<pk>[0-9]+)/confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),
    url(r'^(?P<pk>[0-9]+)/preferences/$', views.PreferenceView.as_view(), name='preferences'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/sendEmail/$', views.sendEmail, name='sendEmail'),
    
    
    url(r'^(?P<pk>[0-9]+)/pollinfo/$', views.PollInfoView.as_view(), name='pollinfo'),
    url(r'^(?P<pk>[0-9]+)/viewvoters/$', views.ViewVotersView.as_view(), name='viewvoters'),
    
]