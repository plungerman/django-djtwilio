# -*- coding: utf-8 -*-

from django.contrib import admin

from djtwilio.core.models import Account
from djtwilio.core.models import Profile
from djtwilio.core.models import Sender


class AccountAdmin(admin.ModelAdmin):
    """Django admin class for Account data model class."""

    list_per_page = 100
    list_display = ('sid', 'token', 'department')
    ordering = ('department',)


class SenderAdmin(admin.ModelAdmin):
    """Django admin class for Sender data model class."""

    list_display = (
        'last_name', 'first_name', 'alias', 'phone', 'messaging_service_sid',
    )
    ordering = ('user__last_name', 'user__first_name', 'phone')
    search_fields = (
        'user__last_name',
        'user__first_name',
        'user__email',
        'user__username',
        'phone',
    )
    list_per_page = 500
    raw_id_fields = ('user',)

    def first_name(self, instance):
        """Return the sender user's first name."""
        return instance.user.first_name

    def last_name(self, instance):
        """Return the sender user's last name."""
        return instance.user.last_name

    def account(self, instance):
        """Return the account with which this sender is associated."""
        return instance.account


class ProfileAdmin(admin.ModelAdmin):
    """Django admin class for Profile data model class."""

    list_display = ('last_name', 'first_name', 'bulk')
    ordering = ('user__last_name', 'user__first_name')
    search_fields = (
        'user__last_name', 'user__first_name', 'user__email', 'user__username',
    )
    list_per_page = 500
    raw_id_fields = ('user',)

    def first_name(self, instance):
        """Return the user's first name."""
        return instance.user.first_name

    def last_name(self, instance):
        """Return the user's last name."""
        return instance.user.last_name


admin.site.register(Account, AccountAdmin)
admin.site.register(Sender, SenderAdmin)
admin.site.register(Profile, ProfileAdmin)
