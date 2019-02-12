# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')

from django.conf import settings

from twilio.rest import Client


def main():
    """
    Create an API Key
    """

    client = Client( settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    new_key = client.new_keys.create()

    print(new_key.sid)


######################
# shell command line
######################

if __name__ == '__main__':

    sys.exit(main())
