from apps.war.views import PVE, PVP, PVP_Calc, Game_Control, PVP_Createbullets
from django.conf.urls import url

urlpatterns = [
    url(r'^pve$', PVE.as_view(), name='pve'),
    url(r'^pvp$', PVP.as_view(), name='pvp'),
    url(r'^pvp_calc$', PVP_Calc.as_view(), name='pvp_calc'),
    url(r'^pvp_createbullets$', PVP_Createbullets.as_view(), name='pvp_createbullets'),
    url(r'^gamecontrol$', Game_Control.as_view(), name='gamecontrol'),
]
