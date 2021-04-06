# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    """Account data model class."""

    sid = models.CharField(max_length=34, null=True, blank=True)
    token = models.CharField(max_length=32, null=True, blank=True)
    department = models.CharField(max_length=24, null=True, blank=True)

    def __unicode__(self):
        """Default display value."""
        return "{0} ({1})".format(self.department, self.sid)


class Sender(models.Model):
    """Sender data model class."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sender',
    )
    phone = models.CharField(
        max_length=12,
        verbose_name="Phone Number",
        null=True,
        blank=True,
    )
    forward_phone = models.CharField(
        max_length=12,
        verbose_name="Forwarding Phone Number",
        null=True,
        blank=True,
    )
    messaging_service_sid = models.CharField(
        max_length=34,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    alias = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )

    def __unicode__(self):
        if self.phone:
            handle = self.phone
        else:
            handle = self.messaging_service_sid
        return "{0} ({1})".format(self.alias, handle)

    def clean(self):
        """Data validation method to determine if a phone or SID is provided."""
        if not self.phone and not self.messaging_service_sid:
            raise ValidationError(
              "You must provide either a phone number of messaging service ID"
            )


class Profile(models.Model):
    """User profile data model class."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bulk = models.BooleanField("Bulk messenger", default=False)

    def __unicode__(self):
        """Default display value."""
        return "{0}, {1}".format(self.user.last_name, self.user.first_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Post-save signal function to create a user profile instance."""
    if created and not kwargs.get('raw', False):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_sender(sender, instance, created, **kwargs):
    """Post-save signal function to create a user sender instance."""
    if created and not kwargs.get('raw', False):
        Sender.objects.create(
            user=instance, alias="{} {}'s SMS sender".format(
                instance.first_name, instance.last_name
            )
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Post-save signal function to save a user's profile instance."""
    if not kwargs.get('raw', False):
        instance.profile.save()
