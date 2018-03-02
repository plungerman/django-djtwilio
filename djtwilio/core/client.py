# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf import settings

from twilio.rest import Client


def twilio_client(account=None):
    """
    Twilio REST client wrapper.
    """

    if account:
        sid = account.sid
        token = account.token
    else:
        sid = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_AUTH_TOKEN

    return Client(sid, token)
