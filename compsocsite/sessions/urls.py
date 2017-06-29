from . import views
from django.contrib.auth.decorators import login_required

app_name = 'sessions'
urlpatterns = [
    #Two main types of polls
    url(r'^$', login_required(views.SessionsMainView.as_view()), name='sessions_main'),
    url(r'^(?P<pk>[0-9]+)/$', views.SessionView.as_view(), name='info'),
]