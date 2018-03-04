from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from djtools.utils.logging import seperator

from djtwilio.apps.sms.models import Error, Message
from djtwilio.core.client import twilio_client
from djtwilio.core.utils import create_test_user

from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException


class AppsSmsViewsTestCase(TestCase):

    fixtures = ['errors.json', 'account.json']

    def setUp(self):

        self.user = create_test_user()
        self.client = twilio_client(self.user.profile.account)
        self.recipient = settings.TWILIO_TEST_PHONE_TO
        self.body = settings.TWILIO_TEST_MESSAGE
        self.mssid_invalid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID_INVALID

    def test_send_valid(self):
        print "\n"
        print "send an sms message"
        seperator()
        die = False
        if settings.DEBUG:
            try:
                response = self.client.messages.create(
                    to = self.recipient,
                    messaging_service_sid = self.user.profile.message_sid,
                    # use parentheses to prevent extra whitespace
                    body = (self.body),
                    status_callback = 'https://requestb.in/19mnap81'
                )
            except TwilioRestException as e:
                die = True
                print "REST Error message:"
                seperator()
                print e

            # create message object
            message = Message.objects.create(
                messenger = self.user,
                recipient = self.recipient,
                body = self.body
            )
            if not die:
                print response.__dict__
                print "response sid:"
                sid = response.sid
                message.message_status.sid = sid
                ms = message.status()
                if ms.status == 'delivered':
                    print "Success: message sent"
                    print message.__dict__
                else:
                    print "Fail: message was not sent: '{}'".format(
                        ms.error_code
                    )
                    error = Error.objects.get(code=ms.error_code)
                    message.message_status.error = error
                    print "Error message: {}".format(
                        message.message_status.error.message
                    )
                    print "Error description: {}".format(
                        message.message_status.error.description
                    )
        else:
            print "use the --debug-mode flag to test message delivery"

    '''
    def test_send_invalid_message_sid(self):
        print "\n"
        print "send an sms message from invalid message sid"
        seperator()
        if settings.DEBUG:
            try:
                response = self.client.messages.create(
                    to = self.to,
                    messaging_service_sid = self.mssid_invalid,
                    # use parentheses to prevent extra whitespace
                    body = (
                        "Test sms message via Python Unit Test\n"
                        "Who does your taxes?"
                    )
                )
            except TwilioRestException as e:
                print "REST Error message:"
                seperator()
                print e

        else:
            print "use the --debug-mode flag to test message delivery"
    '''
