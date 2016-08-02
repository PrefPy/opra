from django.conf.urls import url

from . import views

app_name = 'multipolls'
urlpatterns = [
    # create
    url(r'^add_step1/$', views.AddStep1, name='AddStep1'), 
    url(r'^(?P<pk>[0-9]+)/add_step2/$', views.AddStep2View.as_view(), name='AddStep2'), 
    url(r'^(?P<multipoll_id>[0-9]+)/setquestion/$', views.setQuestion, name='setquestion'),     
    url(r'^(?P<pk>[0-9]+)/add_step3/$', views.AddStep3View.as_view(), name='AddStep3'),
    url(r'^(?P<multipoll_id>[0-9]+)/initial/$', views.setInitialSettings, name='setinitial'), 
    url(r'^(?P<pk>[0-9]+)/setvoters/$', views.SetVotersView.as_view(), name='SetVoters'),
    url(r'^(?P<multipoll_id>[0-9]+)/voter/add$', views.addVoter, name='addvoter'),
    url(r'^(?P<multipoll_id>[0-9]+)/voter/delete$', views.removeVoter, name='delvoter'),
    url(r'^(?P<multipoll_id>[0-9]+)/voter/add/group/$', views.addGroupVoters, name='addGroupVoters'),      
    url(r'^(?P<multipoll_id>[0-9]+)/voter/delete/group/$', views.removeGroupVoters, name='removeGroupVoters'),      
    
    # settings
    url(r'^(?P<pk>[0-9]+)/mpollinfo/$', views.mpollinfoView.as_view(), name='mpollinfo'), 
    url(r'^(?P<multipoll_id>[0-9]+)/delete/$', views.deleteMpoll, name='delmpoll'),
    url(r'^(?P<multipoll_id>[0-9]+)/edit/basic$', views.editBasicInfo, name='editBasicInfo'),

    # start
    url(r'^(?P<multipoll_id>[0-9]+)/progress/$', views.progress, name='progress'), 
    url(r'^(?P<multipoll_id>[0-9]+)/start/$', views.start, name='start'), 
        
    # subpoll voting
    url(r'^dependency/(?P<combination_id>[0-9]+)/get/$', views.getConditionalResponse, name='dependencyget'),
    url(r'^subpoll/(?P<pk>[0-9]+)/dependency/view/$', views.DependencyView.as_view(), name='dependencyview'),
    url(r'^subpoll/(?P<question_id>[0-9]+)/dependency/view/prefgraph$', views.updatePrefGraph, name='updatePrefGraph'),
    url(r'^subpoll/(?P<question_id>[0-9]+)/dependency/choose$', views.chooseDependency, name='choosedependency'),
    url(r'^pref/(?P<combination_id>[0-9]+)/assign$', views.assignPreference, name='assignpreference'),   
]

