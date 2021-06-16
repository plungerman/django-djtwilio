# -*- coding: utf-8 -*-

import csv
import logging
import re
import time

from django.conf import settings
from django.urls import reverse
from djimix.core.encryption import encrypt
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from djtwilio.apps.sms.models import Bulk
from djtwilio.apps.sms.models import Document
from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.models import Status
from djtwilio.core.models import Sender

logger = logging.getLogger(__name__)


def send_message(sid, recipient, body, cid, callback=False, bulk=None, doc=None):
    """Send a message through the twilio api."""
    sender = Sender.objects.filter(pk=sid).first()
    if sender:
        client = Client(sender.account.sid, sender.account.token)
        # this seems like overkill but you never know
        if bulk:
            phrum = sender.messaging_service_sid
        else:
            phrum = sender.phone
            if not phrum:
                phrum = sender.messaging_service_sid
        logger.debug('{0}: {1}'.format(recipient, cid))
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
    else:
        apicall = 'Failed to fetch sender with ID: {0}'.format(sid)
        message = False

    return {'message': message, 'response': apicall}


def send_bulk(bulk, body, phile=None):
    """Send a bulk message through the twilio API."""
    if isinstance(bulk, int):
        bulk = Bulk.objects.get(pk=bulk)
        if phile:
            phile = Document.objects.get(pk=phile)
    rep = 'rep_first'
    indx = None
    # firstname, lastname, phone, cid, rep_first
    with open(bulk.distribution.path, 'r', errors='ignore') as csvfile:
        # check for a header
        has_header = csv.Sniffer().has_header(csvfile.read(1024 * 1024))
        # Rewind.
        csvfile.seek(0)
        # read 1MB chunks to ensure the sniffer works for files
        # of any size without running out of memory:
        dialect = csv.Sniffer().sniff(csvfile.read(1024 * 1024))
        # Rewind.
        csvfile.seek(0)
        # detect delimiter
        delimiter = dialect.delimiter
        # set up csv reader
        reader = csv.reader(
            csvfile, delimiter=delimiter, quoting=csv.QUOTE_NONE,
        )
        # Skip header row.
        if has_header:
            next(reader)
        for row in reader:
            if rep in row:
                indx = row.index(rep)
                # skip header row
            else:
                if indx:
                    body = body.replace(rep, row[indx])
                send_message(
                    bulk.sender.id,
                    row[2],         # recipient
                    body,           # body
                    row[3],         # cid
                    bulk=bulk,
                    doc=phile,
                )
                time.sleep(1)
