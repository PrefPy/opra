from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from . import views
from django.urls import path



app_name = 'mentors'
urlpatterns = [
    url(r'^$', login_required(views.viewindex), name='index'),
    #url(r'^apply$', login_required(views.ApplyView.as_view()), name='apply'),

    # Mentor applciation steps 1-6
    url(r'^apply/$', login_required(views.applystep), name='applyfunc1'),
    url(r'^applystep2/$', login_required(views.applystep2), name='applystep2'),
    url(r'^applystep3/$', login_required(views.applystep3), name='applystep3'),
    url(r'^applystep4/$', login_required(views.applystep4), name='applystep4'),
    url(r'^applystep5/$', login_required(views.applystep5), name='applystep5'),
    url(r'^applystep6/$', login_required(views.applystep6), name='applystep6'),


    url(r'^view-course$', login_required(views.CourseFeatureView.as_view()), name='view-course'),
    url(r'^view-match-result$', login_required(views.MatchResultView.as_view()), name='view-match-result'),

    url(r'^addcoursefunc/$', login_required(views.addcourse), name='addcoursefunc'),
    url(r'^addStudentRandomfunc/$', views.addStudentRandom, name='addStudentRandomfunc'),
    url(r'^matchfunc/$', login_required(views.StartMatch), name='matchfunc'),

    url(r'^searchcoursefunc/$', login_required(views.searchCourse), name='searchcoursefunc'),
    url(r'^changefeaturefunc/$', login_required(views.changeFeature), name='changefeaturefunc'),

    url(r'^view_application$', login_required(views.viewApplictionView.as_view()), name='view_application'),
    url(r'^view-students$', login_required(views.viewStudentsView.as_view()), name='view-students'),
    url(r'^download-mentor-csv/$', login_required(views.download_mentor_csv), name='download-mentor-csv'),
    url(r'^withdrawfunc/$', views.withdraw, name='withdrawfunc'),
    #url(r'^apply_prefernece/$', login_required(views.CourseAutocomplete.as_view()), name='apply_prefernece'),

]   
