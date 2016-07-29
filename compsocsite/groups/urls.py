from django.conf.urls import url

from . import views

app_name = 'groups'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.addGroupView.as_view(), name='addgroup'),
    url(r'^addgroupfunc/$', views.addgroup, name='addgroupfunc'),
    url(r'^delete/([0-9]+)/$', views.deletegroup, name='deletegroup'),
    url(r'^(?P<pk>[0-9]+)/members/$', views.MembersView.as_view(), name='members'),
    url(r'^(?P<group_id>[0-9]+)/members/add/$', views.addmember, name='addmember'),    
    url(r'^(?P<group_id>[0-9]+)/members/remove/$', views.removemember, name='removemember'),
    url(r'^(?P<question_id>[0-9]+)/addgroupvoters/$', views.addgroupvoters, name='addgroupvoters'),    
    url(r'^(?P<question_id>[0-9]+)/removegroupvoters/$', views.removegroupvoters, name='removegroupvoters'),  
]