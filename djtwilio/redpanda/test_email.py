# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djtwilio.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.mail import send_mail
from django.template import loader

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

logger = logging.getLogger('debug_logfile')


def main():
    frum = settings.REDPANDA_SMTP_ACCOUNTS[7]['username']
    subject = "Daily Health Check Reminder"
    earl = 'https://{0}'.format(settings.REDPANDA_SERVER_URL)
    body = settings.REDPANDA_TEXT_MESSAGE(earl=earl)
    print(body)
    for email in [settings.ADMINS[0][1], frum]:
        print(email)
        headers = {'Reply-To': frum, 'From': frum}
        print(headers)
        template = loader.get_template('redpanda/email_reminder.html')
        context_data = {'earl': earl}
        rendered = template.render({'data': context_data}, None)
        try:
            send_mail(
                subject,
                body,
                frum,
                [email],
                auth_user=frum,
                auth_password=settings.REDPANDA_SMTP_ACCOUNTS[7]['password'],
                fail_silently=False,
                html_message=rendered,
            )
        except Exception as e:
            logger.debug(e)


if __name__ == '__main__':

    sys.exit(main())
