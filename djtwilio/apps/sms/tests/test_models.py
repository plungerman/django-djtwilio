from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from djtwilio.apps.sms.models import Message
from djtwilio.core.utils import create_test_user

from djtools.utils.logging import seperator


class AppsSmsModelsTestCase(TestCase):

    fixtures = ['account.json']

    def setUp(self):

        self.user = create_test_user()
        self.recipient = settings.TWILIO_TEST_PHONE_TO
        self.body = settings.TWILIO_TEST_MESSAGE

    def test_message(self):
        print "\n"
        print "create a message object"
        seperator()
        message = Message.objects.create(
            messenger = self.user,
            recipient = self.recipient,
            body = self.body
        )
        #print message.message_status.sid
        print message.message_status.id
