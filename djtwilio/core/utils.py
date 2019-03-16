# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse

from djtwilio.apps.sms.models import Message, Status

from twilio.base.exceptions import TwilioRestException


def send_message(client, sender, recipient, body, cid, callback=False, bulk=None):
    if bulk:
        phrum=sender.messaging_service_sid
    else:
        phrum=sender.phone
    try:
        # create Status object
        status = Status.objects.create()
        # create Message object before API call
        recipient = str(recipient).translate(None, '.+()- ')
        message = Message.objects.create(
            messenger=sender, recipient=recipient,
            student_number=cid, body=body, bulk=bulk, status=status
        )
        message.save()
        # for some reason, when testing, the URL does not include ROOT_URL
        # so we can send a URL from test case and use the proper URL here
        if not callback:
            callback = 'https://{}{}'.format(
                settings.SERVER_URL, reverse(
                    'sms_status_callback', args=[message.id]
                )
            )
        apicall = client.messages.create(
            # use parentheses around body to prevent extra whitespace
            to=recipient, from_=phrum, body=(body), status_callback = callback
        )
        status.SmsSid=status.MessageSid=apicall.sid
        status.SmsStatus=status.MessageStatus=apicall.status
        status.save()
    except TwilioRestException as e:
        apicall = e
        message = False

    return {'message': message, 'response': apicall}
