from django.contrib import admin

from djtwilio.apps.sms.models import (
    Error, Bulk, Message, Status
)


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'messenger', 'recipient', 'bulk', 'date_created', 'status'
    )
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    readonly_fields = ('messenger','bulk')
    search_fields = ('body','recipient','student_number')
    list_per_page = 500
    raw_id_fields = ('messenger', 'status', 'bulk', 'phile')

    def first_name(self, obj):
        return obj.messenger.user.first_name

    def last_name(self, obj):
        return obj.messenger.user.last_name


class ErrorAdmin(admin.ModelAdmin):
    ordering = (
        'code',
    )


class BulkAdmin(admin.ModelAdmin):
    list_display = (
        'sender','name','description','date_created'
    )


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        'To', 'From', 'error', 'date_created', 'MessageStatus'
    )


admin.site.register(Message, MessageAdmin)
admin.site.register(Error, ErrorAdmin)
admin.site.register(Bulk, BulkAdmin)
admin.site.register(Status, StatusAdmin)
