from django.contrib import admin

from djtwilio.apps.sms.models import (
    Error, Bulk, Message, Status
)


class MessageAdmin(admin.ModelAdmin):
    pass
    '''
    list_display = (
        'messenger', 'recipient', 'bulk', 'date_created'
    )
    date_hierarchy = 'date_created'
    ordering = (
        'date_created'
    )
    readonly_fields = (
        'messenger','bulk'
    )
    search_fields = (
        'body'
    )
    list_per_page = 500
    raw_id_fields = ('messenger',)

    def first_name(self, obj):
        return obj.messenger.user.first_name

    def last_name(self, obj):
        return obj.messenger.user.last_name
    '''


class ErrorAdmin(admin.ModelAdmin):
    ordering = (
        'code',
    )


class BulkAdmin(admin.ModelAdmin):
    pass


class StatusAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(Error, ErrorAdmin)
admin.site.register(Bulk, BulkAdmin)
admin.site.register(Status, StatusAdmin)
