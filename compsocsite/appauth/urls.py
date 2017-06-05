from django.conf.urls import url
import cas.middleware

from . import views

app_name = 'appauth'
urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^login/forgetpassword/$', views.forgetPassword, name='forgetpassword'),
    url(r'^login/forgetpasswordview/$', views.forgetPasswordView, name='forgetpasswordview'),
    url(r'^login/forgetpassword/resetpassword/(?P<pk>[0-9]+)/$', views.resetPasswordView.as_view(), name='resetpasswordview'),
    url(r'^login/forgetpassword/resetpassword/action/(?P<user_id>[0-9]+)/$', views.resetPassword, name='resetpassword'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^settings/$', views.displaySettings, name='settings'),
    url(r'^passwordpage/$', views.changePasswordView, name='passwordpage'),
    url(r'^passwordpage/changepassword/$', views.changepassword, name='changepassword'),
    url(r'^settings/global/$', views.globalSettings, name='globalSettings'),
    url(r'^settings/update/$', views.updateSettings, name='updateSettings'),
    url(r'^settings/diablehint/$', views.disableHint, name='disableHint'),
    url(r'^settings/update/global$', views.updateGlobalSettings, name='updateGlobalSettings'),
	url(r'^register/confirm/(?P<user_id>[0-9]+)/$',views.confirm, name='confirm'),
    url(r'^messages$', views.MessageView.as_view(), name='messages'),
]