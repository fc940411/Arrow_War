from apps.users.views import Index, Register
from django.conf.urls import url

urlpatterns = [
    url(r'^index$', Index.as_view(),name='index'),
    url(r'^register$', Register.as_view(),name='register'),
    url(r'', Index.as_view()),
]