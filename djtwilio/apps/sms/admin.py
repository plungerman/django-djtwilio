# -*- coding: utf-8 -*-

from django.contrib import admin

from djtwilio.apps.sms.models import Bulk
from djtwilio.apps.sms.models import Error
from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.models import Status


class MessageAdmin(admin.ModelAdmin):
    """Admin class for the Message data model class."""

    list_display = ('messenger', 'recipient', 'bulk', 'date_created', 'status')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    readonly_fields = ('messenger', 'bulk')
    search_fields = ('body', 'recipient', 'student_number')
    list_per_page = 500
    raw_id_fields = ('messenger', 'status', 'bulk', 'phile')

    def first_name(self, obj):
        """Return the messenger user's first name."""
        return obj.messenger.user.first_name

    def last_name(self, obj):
        """Return the messenger user's last name."""
        return obj.messenger.user.last_name


class ErrorAdmin(admin.ModelAdmin):
    """Admin class for the twilio Error data model class."""

    ordering = ('code',)


class BulkAdmin(admin.ModelAdmin):
    """Admin class for the bulk message data model class."""

    list_display = ('sender','name','description','date_created')


class StatusAdmin(admin.ModelAdmin):
    """Admin class for the twilio status data model class."""

    list_display = ('To', 'From', 'error', 'date_created', 'MessageStatus')


admin.site.register(Message, MessageAdmin)
admin.site.register(Error, ErrorAdmin)
admin.site.register(Bulk, BulkAdmin)
admin.site.register(Status, StatusAdmin)
