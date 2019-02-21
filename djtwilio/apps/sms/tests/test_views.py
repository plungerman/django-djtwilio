from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from djtwilio.apps.sms.data import CtcBlob
from djtwilio.apps.sms.models import Error, Message, Status
from djtwilio.core.utils import send_message

from djtools.utils.logging import seperator
from djtools.utils.cypher import AESCipher
from djzbar.utils.informix import get_session

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from unittest import skip


#@skip("skip for now until bulk test if built")
class AppsSmsViewsTestCase(TestCase):

    fixtures = [
        'errors.json','account.json','status.json','user.json','message.json',
        'profile','sender.json'
    ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)
        self.sender = self.user.sender.get(pk=settings.TWILIO_TEST_SENDER_ID)
        self.twilio = Client(self.sender.account.sid, self.sender.account.token)
        self.recipient = settings.TWILIO_TEST_PHONE_TO
        self.body = settings.TWILIO_TEST_MESSAGE
        self.mssid_invalid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID_INVALID
        self.sid = settings.TWILIO_TEST_MESSAGE_SID
        self.cid = settings.TWILIO_TEST_COLLEGE_ID
        self.earl = settings.INFORMIX_EARL
        self.factory = RequestFactory()

    @skip("skip for now until bulk test if built")
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

    @skip("skip for now until bulk test if built")
    def test_detail(self):

        print("\n")
        print("message detail")

        medium = 'screen'
        user = self.user
        message = Message.objects.get(status__MessageSid=self.sid)
        template = 'apps/sms/detail_{}.html'.format(medium)

    #@skip("skip for now until bulk test if built")
    def test_status_callback(self):

        print("\n")
        print("status callback")
        status_dict = settings.TWILIO_TEST_STATUS_DICT
        cipher = AESCipher(bs=16)
        mid = cipher.encrypt(str(settings.TWILIO_TEST_MESSAGE_ID))
        response = self.client.post(
            reverse('sms_status_callback',args=[mid]), status_dict
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
        '''.format(settings.TWILIO_TEST_COLLEGE_ID, blob.bctc_no)

        print("insert sql statement:\n{}".format(sql))

        session.execute(sql)
        session.commit()

    def test_send_individual_valid(self):
        print("\n")
        print("send an individual sms message")
        seperator()
        if settings.DEBUG:
            #request = self.factory.get(reverse('sms_send_form'))
            cipher = AESCipher(bs=16)
            mid = cipher.encrypt(str(settings.TWILIO_TEST_MESSAGE_ID))
            print("encrypted message ID = {}".format(mid))
            callback = 'https://{}{}{}'.format(
                settings.SERVER_URL, settings.ROOT_URL,
                reverse('sms_status_callback', args=[mid])
            )
            print(callback)
            sent = send_message(
                self.twilio, self.sender, self.recipient, self.body, self.cid,
                callback
            )

            if sent['message']:
                message = sent['message']
                if sent['response'].status == 'delivered':
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
                    #print(sent['response'].__dict__)
                    #print(message.__dict__)
            else:
                print("send message not 'delivered'")
                print(sent['response'])
        else:
            print(
                "{} to {} ({}) from {}".format(
                    self.body, self.recipient, self.cid,
                    self.sender.messaging_service_sid
                )
            )

            print("use the --debug-mode flag to test message delivery")

    @skip("skip for now until bulk test if built")
    def test_send_individual_invalid_message_sid(self):
        print("\n")
        print("send an sms message from invalid message sid")
        seperator()

        if settings.DEBUG:
            try:
                response = self.twilio.messages.create(
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
                print("REST Error message:")
                seperator()
                print(e)
        else:
            print("use the --debug-mode flag to test message delivery")
