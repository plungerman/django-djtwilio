from django.contrib import admin

from djtwilio.core.models import (
    Account, Profile
)


class AccountAdmin(admin.ModelAdmin):
    pass


class ProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Account, AccountAdmin)
admin.site.register(Profile, ProfileAdmin)
