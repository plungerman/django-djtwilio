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
from django.template import loader
from django.core.mail import send_mail
from djimix.core.database import get_connection
from djimix.core.database import xsql
from djtwilio.core.models import Sender
from djtwilio.core.utils import send_message
from twilio.rest import Client


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
    """Send students notification to complete daily health check."""
    logger.debug('start')
    request = None
    frum = settings.DEFAULT_FROM_EMAIL
    subject = "Daily Health Check Reminder:"
    # fetch our students
    phile = os.path.join(settings.BASE_DIR, 'redpanda/students.sql')
    with open(phile) as incantation:
        sql = incantation.read()
        print(sql)
    with get_connection() as connection:
        students = xsql(sql, connection).fetchall()

    # twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    sender = Sender.objects.get(pk=settings.REDPANDA_SENDER_ID)
    print('sender = {0}'.format(sender))
    # fetch our UUID
    mobi = 0
    mail = 0
    smtp_index = 0
    smtp_count = 0
    print('smtp_index = {0}'.format(smtp_index))
    with get_connection(settings.MSSQL_EARL, encoding=False) as mssql_cnxn:
        for student in students:
            sql = "SELECT * FROM fwk_user WHERE HostID like '%{}'".format(student[0])
            row = xsql(sql, mssql_cnxn).fetchone()
            if row:
                '''
                earl = 'https://{0}{1}{2}?uid={3}'.format(
                    settings.REDPANDA_SERVER_URL,
                    settings.REDPANDA_ROOT_URL,
                    settings.REDPANDA_SHORT_URL_API,
                    row[0],
                )
                '''
                earl = 'https://{0}{1}'.format(
                    settings.REDPANDA_SERVER_URL,
                    settings.REDPANDA_ROOT_URL,
                )
                #response = requests.get(earl)
                #jason_data = json.loads(response.text)
                #earl = jason_data['lynx']
                # send an SMS or an email
                body = settings.REDPANDA_TEXT_MESSAGE(earl=earl)
                if settings.DEBUG:
                    print(body)
                if student[6]:
                    response = send_message(client, sender, student[6], body, student[0])
                    if settings.DEBUG:
                        print(response)
                        print(student[6])
                        print(row[0])
                    mobi += 1
                else:
                    auth_user = settings.REDPANDA_SMTP_ACCOUNTS[smtp_index]['username']
                    auth_pass = settings.REDPANDA_SMTP_ACCOUNTS[smtp_index]['password']
                    if smtp_count >= settings.REDPANDA_SMTP_ROTATE_COUNT:
                        smtp_index += 1
                        smtp_count = 0
                        print('smtp_index = {0}'.format(smtp_index))
                    else:
                        smtp_count += 1
                    mail += 1
                    email = student[8]
                    if settings.DEBUG:
                        print(email)
                    logger.debug(student[0])
                    context_data = {'earl': earl, 'student': student}
                    headers = {'Reply-To': frum,'From': frum,}
                    if settings.DEBUG:
                        print(headers)
                    template = loader.get_template('redpanda/email_reminder.html')
                    rendered = template.render({'data':context_data,}, request)
                    try:
                        send_mail(
                            subject,
                            body,
                            frum,
                            [email],
                            fail_silently=False,
                            auth_user=auth_user,
                            auth_password=auth_pass,
                            html_message=rendered,
                        )
                    except Exception as e:
                        print(e)
                        logger.debug(e)
                        logger.debug(student[0])
                        if smtp_count >= 80:
                            smtp_index += 1
                            smtp_count = 0

            else:
                logger.debug('student not found in the portal: {0}'.format(student[0]))

    print(mobi)
    print(mail)


if __name__ == '__main__':

    sys.exit(main())
