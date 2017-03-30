"""compsocsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings
from django.views.static import serve
from polls.views import GMView
from polls.views import sendMessage
from polls.views import CSPosterView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/polls/main')),
    url(r'^polls/', include('polls.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('appauth.urls')),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    url(r'^multipolls/', include('multipolls.urls')),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^GM2017$', GMView.as_view(), name='voting_demo'),
    url(r'^message$', GMView.as_view(), name='message'),
    url(r'^GM2017$', GMView.as_view(), name='GM_2017'),
    url(r'^CSposter$', CSPosterView.as_view(), name='CS_poster'),
]
