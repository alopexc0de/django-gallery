# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.signing import Signer
from django.utils import timezone
from django.conf import settings
from django.db import models

import uuid

# Foreign key to logged-in users
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Account(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    user = models.OneToOneField(AUTH_USER_MODEL,
                                on_delete=models.PROTECT)
    first_login = models.BooleanField(default=True)
    accepted_terms = models.DateTimeField(auto_now=False,
                                          auto_now_add=False,
                                          blank=True,
                                          null=True)

    def __str__(self):
        return "<%s:%s>" % (self.id, self.user.username)

    def create_user(self, username, first_name, last_name, email, password):
        # Create a user
        usr_obj = User.objects.get_or_create(username=username,
                                             first_name=first_name,
                                             last_name=last_name,
                                             email=email)
        usr_obj.set_password(password)
        usr_obj.save()

        self.user = usr_obj
        self.save()

        return self
