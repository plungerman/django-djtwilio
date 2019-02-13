from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from djtwilio.apps.sms.models import Message

from djtools.utils.logging import seperator


class AppsSmsModelsTestCase(TestCase):

    fixtures = [ 'user.json','profile','sender.json','account.json' ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)

    def test_message(self):
        print("\n")
        print("create a message object")
        seperator()
        message = Message.objects.create(
            messenger = self.user.sender.get(default=True),
            recipient = settings.TWILIO_TEST_PHONE_TO,
            body = settings.TWILIO_TEST_MESSAGE
        )
