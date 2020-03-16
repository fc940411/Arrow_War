from apps.users.views import Index, Register, Personal
from django.conf.urls import url

urlpatterns = [
    url(r'^register$', Register.as_view(), name='register'),
	url(r'^personal$', Personal.as_view(), name='personal'),
    url(r'^$', Index.as_view(), name='index'),
]
