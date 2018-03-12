# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from account.models import Account
from django.contrib.auth.models import User


# Create your tests here.

class AccountTestCase(TestCase):
    def setUp(self):
        usr1 = User.objects.create(username='usr1',
                            first_name='test',
                            last_name='1',
                            email='test1@example.com')
        usr2 = User.objects.create(username='usr2',
                            first_name='test',
                            last_name='2',
                            email='test2@example.com')
        Account.objects.create(user=usr1)
        Account.objects.create(user=usr2)

    def test_user_meta_data(self):
        """ Should return some info about these user accounts """
        usr1 = User.objects.get(username='usr1')
        usr_acct1 = Account.objects.get(user=usr1)
        usr2 = User.objects.get(username='usr2')
        usr_acct2 = Account.objects.get(user=usr2)
        self.assertEqual(usr_acct1.get_meta(), {'user': 'usr1', 'first_login': True, 'accepted_terms': None})
        self.assertEqual(usr_acct2.get_meta(), {'user': 'usr2', 'first_login': True, 'accepted_terms': None})
