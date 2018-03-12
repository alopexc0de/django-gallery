# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template import loader
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

_reset_salt = 'portalpwreset'

def _resetPassword(key, email, password):
    signer = Signer(salt="portalpwreset")
    key = signer.unsign(key)
    user = auth.models.User.objects.get(pk=key,email=email)
    user.set_password(password)
    user.save()
    return user

def index(request):
    if not request.user.is_authenticated():
        return _ForceLogout(request, 'Please sign in')

    if hasattr(request.user, 'account'):
        user_account = request.user.account
        if user_account.first_login:
            return _ForceLogout(request,
                                'For your security, please login again and change your password')
        else:
            return _ForceLogout(request,
                                'Your user account is not connected to Account meta-data. Please contact support')

    context = {
        'user_name': user_account.user.username,
        'account_meta': user_account,
        'message': None
    }

    return _ResponseTemplate('account/index.html',
                             request,
                             context=context)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        logintype = request.POST['logintype']

        if logintype in ('admin', 'user'):
            user = auth.authenticate(username=username,
                                     password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    try:
                        user_account = user.account

                        # Is it this user's first login?
                        if user_account.first_login:
                            signer = Signer(salt=_reset_salt)
                            key = signer.sign(user.id)
                            # Make them change their password
                            return HttpResponseRedirect('/account/firstlogin/' + key)

                        # Has the user accepted the TOS?
                        accepted_terms = user_account.accepted_terms
                        if accepted_terms is None:
                            # Make them read it
                            return _ResponseTemplate('account/terms',
                                                     request)

                        # Has the TOS been updated since they accepted it?
                        if accepted_terms is not None and accepted_terms < __get_terms_update():
                            # Make them read it
                            return _ResponseTemplate('account/terms',
                                                     request)
                    # No Account One2One user key
                    except ObjectDoesNotExist:
                        return _ForceLogout(request,
                                            'Your user account is not connected to Account meta-data. Please contact support')

                    # Successful login
                    # TODO: Redirect to the page they were on before loggin in, if any
                    return HttpResponseRedirect('/account/')
                else:
                    return _ForceLogout(request,
                                        'Your user account is not active')
            else:
                return _ForceLogout(request,
                                    'Incorrect Username/Password combination')
        elif logintype in ('http-api', 'ssl-api'):
            # TODO: Certificate based and/or API key authentication
            return _ForceLogout(request,
                                'API Login is not yet supported')
        elif logintype in ('google-auth', 'telegram-auth'):
            # TODO: Third Party login
            return _ForceLogout(request,
                                'Third party login is not yet supported')
        else:
            return _ForceLogout(request,
                                'Invalid Login Type')
    else:
        # Show the login page
        return _ResponseTemplate('/account/login.html',
                                 request)

def logout(request):
    return _ForceLogout(request,
                        'You have been logged out')

# Allows the terms to be updated and presented
def __get_terms_update():
    template = loader.get_template('account/terms.html')
    template = template.template.nodelist[0]
    if '<WithNode>' == repr(template):
        template = template.extra_context['updated'].var
        return dateparse.parse_datetime(template)

def terms(request):
    if hasattr(request.user, 'account'):
        user_account = request.user.account
    else:
        return _ForceLogout(request,
                            'Your user account is not connected to Account meta-data. Please contact support')

    if request.method == 'POST':
        if request.POST['accept_terms'] == 'yes':
            user_account.accepted_terms = timezone.now()
            user_account.save()
            mail.terms(user_account.user.username)
            return HttpResponseRedirect('/account/')
        else:
            return _ForceLogout(request,
                                'You have chosen to not accept the terms. You are now logged out.')

    elif request.method == 'GET':
        terms = user_account.accepted_terms
        terms = terms.isoformat() if terms else '1970'

        context = {
            'user_name': user_account.user.username,
            'last_accepted_terms': terms
        }

        return _ResponseTemplate('account/terms.html',
                                 request,
                                 context=context)

    else:
        return HttpResponseNotAllowed(['POST', 'GET'])
def _send_reset_email(user, password=False, signup=False):
    signer = Signer(salt=_reset_salt)
    key = signer.sign(user.pk)

    mail.passwordreset(user.email, key, password, signup and user.username)

def reset(request, key):
    signer = Signer(salt=_reset_salt)

    if request.method == 'GET':
        if not key:
            try:
                key = signer.sign(request.user.id)
            except IndexError, ValueError:
                return _ForceLogout(request,
                                    'Your password reset key was missing. Please try again')

        key = signer.unsign(key)

        context = {
            'key': signer.sign(key)
        }

        return _ResponseTemplate('account/reset.html',
                                 request,
                                 context=context)
    elif request.method == 'POST':
        if key:
            password = request.POST['password']
            email = request.POST['email']

            if not email or not email:
                return _ResponseTemplate('account/reset.html',
                                         request,
                                         message='You did not provide a valid email or password')

            # Reset the password
            key, user = _resetUserPassword(key, password)

            if not user:
                return _ForceLogout(request, 'Unknown User')

            if not hasattr(request.user, 'account'):
                return _ForceLogout(request,
                                    'Your user account is not connected to Account meta-data. Please contact support')

            return _ForceLogout(request,
                                'Password changed. Please sign in again')
        else:
            data = json.loads(request.body)
            email = data['email']

            try:
                user = auth.models.User.objects.get(email=email)
            except auth.models.User.DoesNotExist:
                return _ForceLogout(request,
                                    'Invalid email address')
            _send_reset_email(user)
            return _ForceLogout(request,
                                'A password reset link has been sent to your email')
    else:
        return HttpResponseNotAllowed(['POST', 'GET'])

def firstlogin(request, key):
    if request.method == 'GET':
        # They should not be here without a key
        if not key:
            return _ForceLogout(request,
                                'Your password reset key was missing. Please try again')

        signer = Signer(salt=_reset_salt)
        username = auth.models.User.objects.get(pk=signer.unsign(key))

        context = {
            'key': key,
            'username': username
        }

        return _ResponseTemplate('account/firstlogin.html',
                                 request,
                                 context=context)
    elif request.method == 'POST':
        if not key:
            return _ForceLogout(request,
                                'Your password reset key was missing. Please try again')
        # Reset the password
        password = request.POST['password']
        email = request.POST['email']

        if not email or not email:
            return _ResponseTemplate('account/firstlogin.html',
                                     request,
                                     message='You did not provide a valid email or password')

        key, user =_resetUserPassword(key, email, password)

        if not user:
            return _ForceLogout(request,
                                'Unknown User')

        try:
            user.account.first_login = False
            user.account.save()
        except ObjectDoesNotExist:
            return _ForceLogout(request,
                                'Your user account is not connected to Account meta-data. Please contact support')
        # Reset complete
        return _ForceLogout(request,
                            'Password changed. Please sign in again')
    else:
        return HttpResponseNotAllowed(['POST', 'GET'])

def create(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    keys = {}
    try:
        fields = [
            'firstname',
            'lastname',
            'email',
            'username',
            'password'
        ]
        req = request.POST
        # Create a signup system
        keys = {x:req[x] for x in fields}

        user_account = Account.objects.create_user(**keys)

        return _ForceLogout(request,
                            'Account Created. Please sign in')
    except KeyError, e:
        context = {
            'error': {
                'code': 'missing_fields',
                'message': json.dumps(repr(e))
            }
        }
        return _ForceLogout(request,
                            context=context)
