from django.db import models
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

from djtools.fields.helpers import upload_to_path

from djtwilio.core.models import Sender

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class Error(models.Model):
    """
    Errors returned from API
    """
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
        return u"[{}] {}".format(
            self.code,
            self.message
        )


class Bulk(models.Model):
    """
    Sending messages in bulk
    """
    sender = models.ForeignKey(
        Sender, on_delete=models.CASCADE,
        related_name='bulk_sender'
    )
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
        upload_to=upload_to_path, max_length=768,
        validators=[
            FileExtensionValidator(allowed_extensions=['csv','CSV'])
        ],
        help_text="""
            CSV File: Last Name, First Name, Phone, College ID,
            separated by a tab
        """
    )

    def __unicode__(self):
        return self.name

    def get_slug(self):
        return 'files/bulk/'


class Status(models.Model):
    """
    POST content from Twilio:
    """
    date_created = models.DateTimeField(
        auto_now_add=True
    )
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
    # deprecated
    SmsSid = models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    # always 2010-04-01 at the moment
    ApiVersion = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    ErrorCode = models.CharField(
        max_length = 16,
        null=True, blank=True
    )
    # values returned from API  when recipient replies to a message
    NumMedia = models.IntegerField(null=True, blank=True)
    ToCity= models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    ToState = models.CharField(
        max_length = 4,
        null=True, blank=True
    )
    ToZip = models.CharField(
        max_length = 12,
        null=True, blank=True
    )
    ToCountry = models.CharField(
        max_length = 4,
        null=True, blank=True
    )
    FromCity= models.CharField(
        max_length = 34,
        null=True, blank=True
    )
    FromState = models.CharField(
        max_length = 4,
        null=True, blank=True
    )
    FromZip = models.CharField(
        max_length = 12,
        null=True, blank=True
    )
    FromCountry = models.CharField(
        max_length = 4,
        null=True, blank=True
    )

    def __unicode__(self):
        return u"{}".format(self.MessageStatus)


class Message(models.Model):
    """
    An SMS data model
    """
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    messenger = models.ForeignKey(
        Sender, on_delete=models.CASCADE,
        related_name='messenger'
    )
    recipient = models.CharField(
        max_length=12
    )
    student_number = models.CharField(
        null=True, blank=True,
        max_length=16
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
        account = self.messenger.profile
        c = Client(account.sid, account.token)
        ms = c.messages(sid).fetch()
        while ms.status != status:
            # we limit the loop to 100 for now. the REST API end point
            # can take some time to return a status, which could be:
            # accepted, queued, sending, sent, receiving, or received.
            # and then finally delivered, undelivered, or failed.
            if count < 100:
                ms = c.messages(sid).fetch()
            else:
                break
            count += 1
            if ms.status == status:
                break

        return ms

    def is_valid_number(self):
        account = self.messenger.profile
        c = Client(account.sid, account.token)
        try:
            response = c.lookups.phone_numbers(self.recipient).fetch(
                type='carrier'
            )
            return True
        except TwilioRestException as e:
            if e.code == 20404:
                return False
            else:
                return e
