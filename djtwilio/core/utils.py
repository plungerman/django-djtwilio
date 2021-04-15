# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.urls import reverse

from djimix.core.encryption import encrypt
from twilio.base.exceptions import TwilioRestException

from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.models import Status


def send_message(client, sender, recipient, body, cid, callback=False, bulk=None, doc=None):
    """Send a message through the twilio api."""
    # this seems like overkill but you never know
    if bulk:
        phrum = sender.messaging_service_sid
    else:
        phrum = sender.phone
        if not phrum:
            phrum = sender.messaging_service_sid
    try:
        # create Status object
        status = Status.objects.create()
        # create Message object before API call
        recipient = re.sub('[^A-Za-z0-9]+', '', recipient)
        message = Message.objects.create(
            messenger=sender,
            recipient=recipient,
            student_number=cid,
            body=body,
            bulk=bulk,
            status=status,
            phile=doc,
        )
        if not callback:
            callback = 'https://{0}{1}'.format(
                settings.SERVER_URL,
                reverse(
                    'sms_status_callback',
                    args=[encrypt(str(message.id))],
                ),
            )
        media_url = []
        if doc:
            media_url = [
                'https://{0}/{1}'.format(settings.SERVER_URL, doc.phile.url),
            ]
        # use parentheses around body value to prevent extra whitespace
        apicall = client.messages.create(
            to=recipient,
            from_=phrum,
            body=(body),
            status_callback=callback,
            media_url=media_url,
        )
        status.SmsSid = apicall.sid
        status.MessageSid = apicall.sid
        status.SmsStatus = apicall.status
        status.MessageStatus = apicall.status
        status.save()
    except TwilioRestException as error:
        apicall = error
        message = False

    return {'message': message, 'response': apicall}
