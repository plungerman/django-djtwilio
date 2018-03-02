from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    sid = models.CharField(
        max_length=34
    )
    token = models.CharField(
        max_length=32
    )
    department = models.CharField(
        max_length=24
    )


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        #related_name='profile_user'
    )
    phone = models.CharField(
        max_length=12, verbose_name="Mobile Number",
        help_text="Format: XXX-XXX-XXXX",
        null=True, blank=True
    )
    message_sid = models.CharField(
        max_length=34,
        null=True, blank=True
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name='profile_account',
        null=True, blank=True
    )
    bulk = models.BooleanField(
        "Bulk messenger",
        default = False
    )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
