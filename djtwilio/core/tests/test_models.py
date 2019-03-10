from django.conf import settings
from django.test import TestCase

from djtools.utils.logging import seperator

from unittest import skip


@skip("skip for now until bulk test is built")
class CoreModelsTestCase(TestCase):

    fixtures = [
        'errors.json','account.json','status.json','user.json','message.json',
        'profile','sender.json'
    ]

    def setUp(self):
        pass

    def test_user_account(self):
        print "\n"
        print "create a user and profile and account"
        seperator()
        print self.sender.account.token
