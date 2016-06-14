from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.addView, name='add'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<question_id>[0-9]+)/addvoter/$', views.addvoter, name='addvoter'),
    url(r'^(?P<pk>[0-9]+)/confirmation/$', views.ConfirmationView.as_view(), name='confirmation'),
    url(r'^(?P<pk>[0-9]+)/preferences/$', views.PreferenceView.as_view(), name='preferences'),
    url(r'^(?P<group_id>[0-9]+)/addmember/$', views.addmember, name='addmember'),
    url(r'^addgroup/$', views.addGroupView.as_view(), name='addgroup'),
    url(r'^(?P<pk>[0-9]+)/members/$', views.MembersView.as_view(), name='members'),
    url(r'^addgroupfunc/$', views.addgroup, name='addgroupfunc'),
    url(r'^edit/$', views.EditView.as_view(), name='edit'),
    url(r'^edit/([0-9]+)/$', views.editAction, name = 'action'),
]