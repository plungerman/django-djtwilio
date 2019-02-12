# -*- coding: utf-8 -*-
import os, sys

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


def main():
    """
    Send an SMS from a messaging service SID
    """

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=settings.TWILIO_TEST_MESSAGING_SERVICE_SID,
        body='who does your taxes?',
        to=settings.TWILIO_TEST_PHONE_TO,
        status_callback = 'https://{}{}{}'.format(
            settings.SERVER_URL, settings.ROOT_URL, reverse('sms_status_callback')
        )
    )

    print(message.__dict__)
    print(message.sid)


######################
# shell command line
######################

if __name__ == '__main__':

    sys.exit(main())
