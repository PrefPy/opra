from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.addView, name='add'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<question_id>[0-9]+)/choice/add/$', views.addChoice, name='addchoice'),
    url(r'^choice/delete/([0-9]+)/$', views.deleteChoice, name='delchoice'),
    url(r'^(?P<question_id>[0-9]+)/addvoter/$', views.addvoter, name='addvoter'),
    url(r'^(?P<pk>[0-9]+)/settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<pk>[0-9]+)/confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),
    url(r'^(?P<pk>[0-9]+)/preferences/$', views.PreferenceView.as_view(), name='preferences'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    
    url(r'^(?P<group_id>[0-9]+)/addmember/$', views.addmember, name='addmember'),
    url(r'^addgroup/$', views.addGroupView.as_view(), name='addgroup'),
    url(r'^(?P<pk>[0-9]+)/members/$', views.MembersView.as_view(), name='members'),
    url(r'^addgroupfunc/$', views.addgroup, name='addgroupfunc'),
    url(r'^(?P<question_id>[0-9]+)/addgroupvoters/$', views.addgroupvoters, name='addgroupvoters'),
    url(r'^(?P<question_id>[0-9]+)/sendEmail/$', views.sendEmail, name='sendEmail'),
]