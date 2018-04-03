from django.contrib import admin

from djtwilio.core.models import Account, Profile, Sender


class AccountAdmin(admin.ModelAdmin):
    pass


class SenderAdmin(admin.ModelAdmin):
    list_display = (
        'last_name','first_name','message_sid'
    )
    ordering = (
        'user__last_name','user__first_name',
    )
    search_fields = (
        'user__last_name','user__first_name','user__email','user__username'
    )
    list_per_page = 500
    raw_id_fields = ('user',)

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def account(self, obj):
        return obj.account


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'last_name','first_name','bulk'
    )
    ordering = (
        'user__last_name','user__first_name',
    )
    search_fields = (
        'user__last_name','user__first_name','user__email','user__username'
    )
    list_per_page = 500
    raw_id_fields = ('user',)

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name


admin.site.register(Account, AccountAdmin)
admin.site.register(Sender, SenderAdmin)
admin.site.register(Profile, ProfileAdmin)
