from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from djtools.fields.helpers import upload_to_path

from djtwilio.core.client import twilio_client
from twilio.base.exceptions import TwilioRestException


class Error(models.Model):
    code = models.CharField(
        max_length=8
    )
    message = models.CharField(
        max_length=64
    )
    description = models.CharField(
        max_length=768
    )

    def __unicode__(self):
        return "[{}] {}".format(
            self.code,
            self.message
        )


class Bulk(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True
    )
    name = models.CharField(
        max_length=64
    )
    description = models.TextField(
        null=True, blank=True
    )
    distribution = models.FileField(
        "Distribution CSV File",
        upload_to=upload_to_path,
        max_length=768,
        help_text="CSV File"
    )


class Status(models.Model):
    '''
        POST content from Twilio:
    '''

    error = models.ForeignKey(
        Error,
        related_name='message_error',
        null=True, blank=True,
    )
    To = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    From = models.CharField(
        max_length=16,
        null=True, blank=True
    )
    MessagingServiceSid = models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    SmsSid = models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    MessageStatus = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    AccountSid = models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    SmsStatus = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    MessageSid = models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    ApiVersion = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    ErrorCode = models.CharField(
        max_length = 16,
        null=True, blank=True
    )


class Message(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True
    )
    messenger = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='message_messenger'
    )
    recipient = models.CharField(
        max_length=12
    )
    body = models.TextField(
        null=True, blank=True
    )
    bulk = models.ForeignKey(
        Bulk, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='message_bulk'
    )
    status = models.ForeignKey(
        Status, on_delete=models.CASCADE,
        related_name='message_status',
        null=True, blank=True
    )

    def get_status(self):

        count = 0
        sid = self.status.MessageSid
        status = 'delivered'
        client = twilio_client(self.messenger.profile.account)
        ms = client.messages(sid).fetch()
        while ms.status != status:
            # we limit the loop to 100 for now. the REST API end point
            # can take some time to return a status, which could be:
            # accepted, queued, sending, sent, receiving, or received.
            # and then finally delivered, undelivered, or failed.
            if count < 100:
                ms = client.messages(sid).fetch()
            else:
                break
            count += 1
            if ms.status == status:
                break

        return ms

    def is_valid_number(self):
        client = twilio_client(self.messenger.profile.account)
        try:
            response = client.lookups.phone_numbers(self.recipient).fetch(
                type='carrier'
            )
            return True
        except TwilioRestException as e:
            if e.code == 20404:
                return False
            else:
                return e
