# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from gallery.utility import _ResponseTemplate, _ForceLogout
from django.conf import settings
from django.contrib import auth

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseNotAllowed
from django.utils import timezone, dateparse
from rest_framework import views, response, status
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist

import json

from .models import *

def _resetPassword(key, password):
    signer = Signer(salt="portalpwreset")
    key = signer.unsign(key)
    user = auth.models.User.objects.get(pk=key)
    user.set_password(password)
    user.save()
    return user

def index(request):
    # if not request.user.is_authenticated():
    #     return _ForceLogout(request, 'Please sign in')
    pass

def login(request):
    pass

def logout(request):
    pass

def terms(request):
    pass

def reset(request):
    pass

def firstlogin(request):
    pass

def create(request):
    pass
