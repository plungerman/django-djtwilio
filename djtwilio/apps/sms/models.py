from django.db import models
from django.contrib.auth.models import User

from djtools.fields.helpers import upload_to_path


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


class Status(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE,
        related_name='message_status'
    )
    sid = models.CharField(
        max_length=34,
        null=True, blank=True
    )
    status = models.CharField(
        max_length=12
    )
    error_code = models.ForeignKey(
        Error,
        null=True, blank=True,
        related_name='message_error'
    )
    phone_from = models.CharField(
        max_length=12,
        null=True, blank=True
    )

