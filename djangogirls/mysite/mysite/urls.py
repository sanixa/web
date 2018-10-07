"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
#from trips.views import hello_world
from content.views import *
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^hello/$', hello_world),
    url(r'^modsecurity/', modsecurity),
    url(r'^index/', index),
    url(r'^mod_l/', mod_l),
    url(r'^mod_m/re/', mod_m_re),
    url(r'^mod_m/', mod_m),
    url(r'^route/', route),
    url(r'^route_config/', route_config),
    url(r'^command/', command),
    url(r'^command_config', command_config),
    url(r'^temp/', temp),
]
