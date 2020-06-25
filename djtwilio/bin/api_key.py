#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from django.conf import settings
from twilio.rest import Client


def main():
    """Create an API Key."""
    client = Client( settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    new_key = client.new_keys.create()
    print(new_key.sid)


if __name__ == '__main__':

    sys.exit(main())
