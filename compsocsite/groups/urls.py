from django.conf.urls import url

from . import views

app_name = 'groups'
urlpatterns = [
    url(r'^add/$', views.addGroupView.as_view(), name='addgroup'),
    url(r'^addgroupfunc/$', views.addgroup, name='addgroupfunc'),
    url(r'^(?P<pk>[0-9]+)/members/$', views.MembersView.as_view(), name='members'),
    url(r'^(?P<group_id>[0-9]+)/members/add/$', views.addmember, name='addmember'),    
    url(r'^(?P<question_id>[0-9]+)/addgroupvoters/$', views.addgroupvoters, name='addgroupvoters'),    
]