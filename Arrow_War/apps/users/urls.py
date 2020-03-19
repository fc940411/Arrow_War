from apps.users.views import Index, Register, Personal, Register_Active
from django.conf.urls import url


urlpatterns = [
    url(r'^register$', Register.as_view(), name='register'),
	url(r'^personal$', Personal.as_view(), name='personal'),
	url(r'^active/(?P<token>.*)', Register_Active.as_view(), name='active'),
    url(r'^$', Index.as_view(), name='index'),
]
