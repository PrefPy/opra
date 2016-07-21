from django.conf.urls import url

from . import views

app_name = 'multipolls'
urlpatterns = [
    url(r'^add_step1/$', views.AddStep1, name='AddStep1'), 
    url(r'^(?P<pk>[0-9]+)/add_step2/$', views.AddStep2View.as_view(), name='AddStep2'), 
    url(r'^(?P<pk>[0-9]+)/add_step3/$', views.AddStep3View.as_view(), name='AddStep3'),
    url(r'^(?P<pk>[0-9]+)/add_step4/$', views.AddStep4View.as_view(), name='AddStep4'),
    url(r'^(?P<pk>[0-9]+)/setvoters/$', views.SetVotersView.as_view(), name='SetVoters'),
    url(r'^(?P<multipoll_id>[0-9]+)/initial/$', views.setInitialSettings, name='setinitial'), 
    url(r'^(?P<multipoll_id>[0-9]+)/addvoter/$', views.addVoter, name='addvoter'),
    url(r'^(?P<multipoll_id>[0-9]+)/delvoter/$', views.removeVoter, name='delvoter'),
    url(r'^(?P<multipoll_id>[0-9]+)/progress/$', views.progress, name='progress'), 
    url(r'^(?P<multipoll_id>[0-9]+)/setquestion/$', views.setQuestion, name='setquestion'), 
    url(r'^(?P<multipoll_id>[0-9]+)/start/$', views.start, name='start'), 
     url(r'^(?P<pk>[0-9]+)/mpollinfo/$', views.mpollinfoView.as_view(), name='mpollinfo'), 
    url(r'^(?P<multipoll_id>[0-9]+)/delete/$', views.deleteMpoll, name='delmpoll'),

    
]