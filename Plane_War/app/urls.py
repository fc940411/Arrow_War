from app import views
from django.conf.urls import url

urlpatterns = [
    url(r'^index$', views.index),
    url(r'^register$', views.register),
    url(r'^register_handle$', views.register_handle),
    url(r'^personal$', views.personal),
    url(r'^personal_handle$', views.personal_handle),
    url(r'^war$', views.war),
    url(r'^war_handle$', views.war_handle),
    url(r'^war_test$', views.war_test),
    url(r'^war_test_handle$', views.war_test_handle),
    url(r'^plane_handle$', views.plane_handle),
    url(r'^login_check$', views.login_check),
    url(r'^set_session$', views.set_session),
    url(r'^logout$', views.logout),
    url(r'^position_calc$', views.position_calc),
    url(r'^enermys_create$', views.enermys_create),
    url(r'^bullets_create$', views.bullets_create),




    url(r'', views.index),
]
