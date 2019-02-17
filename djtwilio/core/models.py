from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    sid = models.CharField(
        max_length=34,
        null=True, blank=True
    )
    token = models.CharField(
        max_length=32,
        null=True, blank=True
    )
    department = models.CharField(
        max_length=24,
        null=True, blank=True
    )

    def __unicode__(self):
        return "{} ({})".format(self.department, self.sid)


class Sender(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sender'
    )
    phone = models.CharField(
        max_length=12, verbose_name="Phone Number",
        help_text="Format: XXX-XXX-XXXX",
        null=True, blank=True
    )
    messaging_service_sid = models.CharField(
        max_length=34,
        null=True, blank=True
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        null=True, blank=True
    )
    nickname = models.CharField(
        max_length=128,
        null=True, blank=True
    )

    def __unicode__(self):
        return "{} [{}] ({})".format(
            self.phone, self.messaging_service_sid, self.nickname
        )

    def clean(self):
        if not self.phone and not self.messaging_service_sid:
            raise ValidationError(
              "You must provide either a phone number of messaging service ID"
            )


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
    )
    bulk = models.BooleanField(
        "Bulk messenger",
        default = False
    )

    def __unicode__(self):
        return "{}, {}".format(
            self.user.last_name, self.user.first_name
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_sender(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        Sender.objects.create(
            user=instance, nickname="{} {}'s Phone".format(
                instance.first_name, instance.last_name
            )
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        instance.profile.save()
