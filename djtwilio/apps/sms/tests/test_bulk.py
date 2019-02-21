from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djtwilio.apps.sms.models import Bulk, Error, Message, Status
from djtwilio.core.utils import send_message

from djtools.utils.logging import seperator

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from unittest import skip

import csv
import os



@skip("skip for now until bulk test if built")
class AppsSmsBulkTestCase(TestCase):

    fixtures = [
        'errors.json','account.json','status.json','user.json','message.json',
        'profile','sender.json'
    ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)
        self.sender = self.user.sender.get(pk=settings.TWILIO_TEST_BULK_SENDER_ID)
        self.twilio = Client(self.sender.account.sid, self.sender.account.token)
        self.bulk_name = settings.TWILIO_TEST_BULK_NAME
        self.bulk_description = settings.TWILIO_TEST_BULK_DESCRIPTION
        self.recipient = settings.TWILIO_TEST_PHONE_TO
        self.body = settings.TWILIO_TEST_MESSAGE
        self.mssid_invalid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID_INVALID
        self.sid = settings.TWILIO_TEST_MESSAGE_SID
        self.earl = settings.INFORMIX_EARL

    def test_send_bulk_valid(self):
        print("\n")
        print("send an sms message en masse")
        seperator()
        die = False
        phile = '{}/{}'.format(
            os.path.dirname(os.path.abspath(__file__)), 'sms.csv'
        )
        bulk = Bulk(
            user=self.user, name=self.bulk_name, distribution=phile,
            description=self.bulk_description
        )
        bulk.save()
        print("bulk object = {}".format(bulk.__dict__))
        with open(phile, 'rb') as f:
            reader = csv.reader(f, delimiter='|', quoting=csv.QUOTE_NONE)
            for r in reader:
                body = "greetings {} {},\n{}".format(r[1], r[0], self.body)
                if settings.DEBUG:
                    callback = 'https://{}{}{}'.format(
                        settings.SERVER_URL, settings.ROOT_URL,
                        reverse(
                            'sms_status_callback',
                            args=[settings.TWILIO_TEST_MESSAGE_ID]
                        )
                    )
                    sent = send_message(
                      self.twilio, self.sender, r[2], body, r[3], callback, bulk
                    )
                    if sent['message']:
                        message = sent['message']
                        if sent['response'] == 'delivered':
                            print("""Your message has been sent. View the
                                <a data-target="#messageStatus" data-toggle="modal"
                                data-load-url="{}" class="message-status text-primary">
                                message status</a>.
                            """.format(
                                reverse('sms_detail',args=[message.status.MessageSid,'modal'])
                            ))
                            print(message.__dict__)
                        else:
                            print("message status was not 'delivered': {}".format(message.status))
                            print(message.status)
                            print(sent['response'].__dict__)
                            print(message.__dict__)
                    else:
                        print("send message failed")
                        print(sent['response'])
                else:
                    print(
                        "{} to {} ({}) from {}".format(
                            body, r[2], r[3], self.sender.messaging_service_sid
                        )
                    )
                    print("use the --debug-mode flag to test message delivery")
