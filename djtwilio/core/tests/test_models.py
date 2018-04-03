from django.conf import settings
from django.test import TestCase

from djtwilio.core.utils import create_test_user

from djtools.utils.logging import seperator


class CoreModelsTestCase(TestCase):

    fixtures = ['account.json']

    def setUp(self):

        self.user = create_test_user()
        self.account = self.user.sender.get(
            account__sid=settings.TWILIO_ACCOUNT_SID
        ).account

    def test_user_account(self):
        print "\n"
        print "create a user and profile and account"
        seperator()
        print self.sender.account.token
