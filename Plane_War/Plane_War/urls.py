"""Plane_War URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from app import views
from django.conf.urls import url,include

urlpatterns = [
    path('admin', admin.site.urls),
    # path('index', views.index),
    # path('', views.index),
    # path('register', views.register),
    # path('personal', views.personal),
    # path('war', views.war),
    url(r'^index', include('app.urls')),
    url(r'^', include('app.urls')),
    # url(r'^register', include('app.urls')),
    # url(r'^register_handle', include('app.urls')),
    # url(r'^personal', include('app.urls')),
    #  url(r'^personal_handle', include('app.urls')),
    # url(r'^war', include('app.urls')),
    # url(r'^login_check', include('app.urls'))
]
