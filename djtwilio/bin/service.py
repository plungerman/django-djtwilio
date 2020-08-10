#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import django
import requests
import sys


django.setup()

from django.conf import settings
from django.core.urlresolvers import reverse

from twilio.rest import Client

# set up command-line options
desc = """
    Send an SMS from a messaging service SID
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-p',
    '--phone',
    required=True,
    help="Phone number to which we are sending the SMS",
    dest='phone',
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Send an SMS from a messaging service SID."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    status_callback_url = 'https://{0}{1}{2}'.format(
        settings.SERVER_URL,
        settings.ROOT_URL,
        reverse('sms_status_callback', args=[666]),
    )
    if test:
        #print(reverse('sms_status_callback', args=[666]))
        #print(request.build_absolute_uri(reverse('sms_status_callback', args=(666, )))
        #request = requests.get(reverse('sms_status_callback', args=(666, )))
        #print(request.text)
        print(status_callback_url)
        print(phone)
    else:
        print(status_callback_url)
        message = client.messages.create(
            from_=settings.TWILIO_TEST_MESSAGING_SERVICE_SID,
            to=phone,
            body='who does your taxes?',
            status_callback=status_callback_url,
        )

        print(message.__dict__)
        print(message.sid)


if __name__ == '__main__':

    args = parser.parse_args()
    phone = args.phone
    test = args.test

    if test:
        print(args)

    sys.exit(main())
