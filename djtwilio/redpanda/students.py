# -*- coding: utf-8 -*-

import os
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djtwilio.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from djimix.core.database import get_connection
from djimix.core.database import xsql
from djimix.core.encryption import encrypt
from djtools.utils.mail import send_mail
from djtwilio.apps.sms.models import Message
from djtwilio.core.models import Sender
from djtwilio.core.utils import send_message
from twilio.rest import Client


def main():
    """Send students notification to complete daily health check."""
    request = None
    frum = settings.DEFAULT_FROM_EMAIL
    subject = "[Health Check] Daily Reminder"
    # fetch our students
    #phile = os.path.join(settings.BASE_DIR, 'redpanda/students.sql')
    phile = os.path.join(settings.BASE_DIR, 'redpanda/staff.sql')
    with open(phile) as incantation:
        sql = '{0} {1}'.format(incantation.read(), settings.REDPANDA_TEST_CIDS)
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
    base = """
        Greetings {first_name},\n\nPlease log your daily health check today:\n\n{earl}\n\nThank you.
    """.format
    with get_connection(settings.MSSQL_EARL, encoding=False) as mssql_cnxn:
        for student in students:
            sql = "SELECT * FROM fwk_user WHERE HostID like '%{}'".format(student[0])
            row = xsql(sql, mssql_cnxn).fetchone()
            if row:
                earl = 'https://{0}{1}?uid={2}'.format(
                    settings.REDPANDA_SERVER_URL,
                    settings.REDPANDA_ROOT_URL,
                    encrypt(row[0]),
                )
                # send an SMS or an email
                #if student.mobile:
                if student[6]:
                    body = base(first_name=student[2], earl=earl)
                    print(body)
                    response = send_message(client, sender, student[6], body, row[0])
                    #print(student[6])
                    #print(row[0])
                    mobi += 1
                else:
                    email = '{0}@carthage.edu'.format(student[8])
                    mail += 1
                    print(email)
                    context_data = {'earl': earl, 'peep': student}
                    '''
                    send_mail(
                        request,
                        [email],
                        subject,
                        frum,
                        'redpanda/email_reminder.html',
                        context_data,
                    )
                    '''
            else:
                print('student not found in the portal: {0}'.format(student[0]))

    print(mobi)
    print(mail)


if __name__ == '__main__':

    sys.exit(main())
