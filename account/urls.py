# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^terms$', views.terms, name='terms'),
    url(r'^reset/(?P<key>[a-zA-Z0-9:_-]*)$', views.reset, name='reset'),
    url(r'^firstlogin/(?P<key>[a-zA-Z0-9:_-]*)$', views.firstlogin, name='firstlogin'),
    url(r'^create$', views.create, name='reset'),
]
