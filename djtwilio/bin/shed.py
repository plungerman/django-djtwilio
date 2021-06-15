#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import os
import sys
from datetime import datetime
from datetime import timedelta

django.setup()

from django.conf import settings
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import schedule

# env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djtwilio.settings.shell")


def main():
    """Testing task queue."""
    body = 'La soledad es la gran talladora del espíritu.'
    sender = settings.TWILIO_TEST_SENDER_ID
    to = settings.TWILIO_TEST_PHONE_TO
    cid = settings.TWILIO_TEST_COLLEGE_ID
    now = datetime.now()
    next_run = timezone.now() + timedelta(minutes=1)
    sched = Schedule.objects.create(
        func='djtwilio.core.utils.send_message',
        args=(sender, to, body, cid),
        schedule_type=Schedule.ONCE,
        next_run=next_run,
        repeats=1,
        name='lorca: {0}'.format(now),
    )
    """
    sched = schedule(
        'djtwilio.core.utils.send_message',
        sender,
        to,
        body,
        cid,
        schedule_type=Schedule.ONCE,
        next_run=next_run,
        repeats=1,
        name='lorca: {0}'.format(now),
    )
    """
    print(sched.__dict__)


if __name__ == "__main__":

    sys.exit(main())
