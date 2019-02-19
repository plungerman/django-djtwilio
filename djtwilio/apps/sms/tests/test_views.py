from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djtwilio.apps.sms.data import CtcBlob
from djtwilio.apps.sms.models import Error, Message, Status
from djtwilio.core.client import twilio_client

from djtools.utils.logging import seperator
from djzbar.utils.informix import get_session

from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException


class AppsSmsViewsTestCase(TestCase):

    fixtures = [
        'errors.json','account.json','status.json','user.json','message.json',
        'profile','sender.json'
    ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)
        sender = self.user.sender.get(pk=settings.TWILIO_TEST_SENDER_ID)
        self.twilio_client = twilio_client(sender.account)
        self.recipient = settings.TWILIO_TEST_PHONE_TO
        self.body = settings.TWILIO_TEST_MESSAGE
        self.mssid_invalid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID_INVALID
        self.sid = settings.TWILIO_TEST_MESSAGE_SID
        self.earl = settings.INFORMIX_EARL

    def test_list(self):

        print("\n")
        print("messages list")

        user = self.user
        all_messages = Message.objects.all().order_by('date_created')
        messages = []
        for sender in user.sender.all():
            for m in sender.messenger.all().order_by('-date_created'):
                print(m)
                messages.append(m)

    def test_detail(self):

        print("\n")
        print("message detail")

        medium = 'screen'
        user = self.user
        message = Message.objects.get(status__MessageSid=self.sid)
        template = 'apps/sms/detail_{}.html'.format(medium)

    def test_status_callback(self):

        print("\n")
        print("status callback")
        status_dict = settings.TWILIO_TEST_STATUS_DICT
        response = self.client.post(
            reverse('sms_status_callback'), status_dict
        )
        print(response)

        print("update informix")

        # create the ctc_blob object with the value of the message body for txt
        session = get_session(self.earl)
        blob = CtcBlob(txt=self.body)
        session.add(blob)
        session.flush()

        sql = '''
            INSERT INTO ctc_rec
                (id, tick, add_date, due_date, cmpl_date, resrc, bctc_no, stat)
            VALUES
                ({},"ADM",TODAY,TODAY,TODAY,"TEXTOUT",{},"C")
        '''.format(settings.TWILIO_TEST_STUDENT_ID, blob.bctc_no)

        print("insert sql statement:\n{}".format(sql))

        session.execute(sql)
        session.commit()

    def test_send_valid(self):
        print("\n")
        print("send an sms message")
        seperator()
        die = False
        if settings.DEBUG:
            try:
                response = self.twilio_client.messages.create(
                    to = self.recipient,
                    messaging_service_sid = self.user.profile.message_sid,
                    # use parentheses to prevent extra whitespace
                    body = (self.body),
                    status_callback = 'https://{}{}'.format(
                        settings.SERVER_URL,
                        reverse('sms_status_callback')
                    )
                )
            except TwilioRestException as e:
                die = True
                print("REST Error message:")
                seperator()
                print(e)

            if not die:
                # create message object
                message = Message.objects.create(
                    messenger = self.user,
                    recipient = self.recipient,
                    body = self.body
                )
                print(response.__dict__)
                print("response sid:")
                sid = response.sid
                status = Status.objects.create(SmsSid=sid, MessageSid=sid)
                message.status = status
                message.save()
                ms = message.get_status()
                if ms.status == 'delivered':
                    print("Success: message sent")
                    print(message.__dict__)
                else:
                    error = Error.objects.get(code=ms.error_code)
                    message.status.error = error
                    print("Fail: message was not sent: '{}'".format(
                        ms.error_code
                    ))
                    print("Error message: {}".format(
                        message.status.error.message
                    ))
                    print("Error description: {}".format(
                        message.status.error.description
                    ))
        else:
            print("use the --debug-mode flag to test message delivery")

    def test_send_invalid_message_sid(self):
        print("\n")
        print("send an sms message from invalid message sid")
        seperator()

        if settings.DEBUG:

            try:
                response = self.twilio_client.messages.create(
                    to = self.recipient,
                    messaging_service_sid = self.mssid_invalid,
                    # use parentheses to prevent extra whitespace
                    body = (self.body),
                    status_callback = 'https://{}{}'.format(
                        settings.SERVER_URL,
                        reverse('sms_status_callback')
                    )
                )
            except TwilioRestException as e:
                die = True
                print("REST Error message:")
                seperator()
                print(e)
        else:
            print("use the --debug-mode flag to test message delivery")
