# -*- coding: utf-8 -*-
import os, sys
import argparse

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')

# prime the app
import django
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
    '-p', '--phone',
    required=True,
    help="Phone number to which we are sending the SMS",
    dest='phone'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    """
    Called when executed from command line
    """

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    status_callback_url = 'https://{}{}{}'.format(
        settings.SERVER_URL, settings.ROOT_URL, reverse('sms_status_callback')
    )
    if test:
        print(status_callback_url)
        print(phone)
    else:
        message = client.messages.create(
            from_=settings.TWILIO_TEST_MESSAGING_SERVICE_SID, to=phone,
            body='who does your taxes?',
            status_callback = status_callback_url
        )

        print(message.__dict__)
        print(message.sid)


######################
# shell command line
######################

if __name__ == '__main__':

    args = parser.parse_args()
    phone = args.phone
    test = args.test

    if test:
        print args

    sys.exit(main())
