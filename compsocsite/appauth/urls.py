from django.conf.urls import url

from . import views

app_name = 'appauth'
urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^restricted/', views.restricted, name='restricted'),    
]