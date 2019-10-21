from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from . import views
from django.urls import path



app_name = 'mentors'
urlpatterns = [
    url(r'^$', login_required(views.IndexView.as_view()), name='index'),
    url(r'^apply$', login_required(views.ApplyView.as_view()), name='apply'),
    # personal info
    url(r'^applyfunc1/$', views.applystep, name='applyfunc1'),
    # compensation and responsbility
    url(r'^applyfunc2/$', views.applystep, name='applyfunc2'),
    # RANKING of preference of course of studnet
    url(r'^applyfunc3/$', views.applystep, name='applyfunc3'),

    url(r'^view_application$', login_required(views.view_applyView.as_view()), name='view_application'),
    url(r'^withdrawfunc/$', views.withdraw, name='withdrawfunc'),
    url(r'^apply_personal_info$', login_required(views.ApplyPersonalInfoView.as_view()), name='apply_personal_info'),
    url(r'^apply_compensation$', login_required(views.ApplyCompensationView.as_view()), name='apply_compensation'),
    url(r'^apply_prefernece$', login_required(views.ApplyPreferenceView.as_view()), name='apply_prefernece'),

]   
