from apps.war.views import PVE, PVP
from django.conf.urls import url

urlpatterns = [
    url(r'^pve$', PVE.as_view(), name='pve'),
	url(r'^pvp$', PVP.as_view(), name='pvp'),
]
