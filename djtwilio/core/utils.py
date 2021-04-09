# -*- coding: utf-8 -*-

from django.conf import settings
from django.urls import reverse
from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.models import Status
from djtools.utils.cypher import AESCipher
from twilio.base.exceptions import TwilioRestException


def send_message(client, sender, recipient, body, cid, callback=False, bulk=None, doc=None):
    """Send a message through the twilio api."""
    # this seems like overkill but you never know
    if bulk:
        phrum=sender.messaging_service_sid
    else:
        phrum=sender.phone
        if not phrum:
            phrum = sender.messaging_service_sid
    try:
        # create Status object
        status = Status.objects.create()
        # create Message object before API call
        recipient = str(recipient).translate(None, '.+()- ')
        message = Message.objects.create(
            messenger=sender,
            recipient=recipient,
            student_number=cid,
            body=body,
            bulk=bulk,
            status=status,
            phile=doc,
        )
        cipher = AESCipher(bs=16)
        if not callback:
            callback = 'https://{0}{1}'.format(
                settings.SERVER_URL,
                reverse(
                  'sms_status_callback', args=[cipher.encrypt(str(message.id))],
                ),
            )
        # mediaUrl=['https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg'],
        media_url = []
        if doc:
            media_url = ['https://{0}/{1}'.format(settings.SERVER_URL, doc.phile.url)]
        # use parentheses around body value to prevent extra whitespace
        apicall = client.messages.create(
            to=recipient,
            from_=phrum,
            body=(body),
            status_callback=callback,
            media_url=media_url,
        )
        status.SmsSid=status.MessageSid=apicall.sid
        status.SmsStatus=status.MessageStatus=apicall.status
        status.save()
    except TwilioRestException as error:
        apicall = error
        message = False

    return {'message': message, 'response': apicall}
