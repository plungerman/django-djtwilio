from django.conf import settings
from django.contrib.auth.models import Group, User

from djtwilio.core.models import Account


def create_test_user():

    # create the auth user
    user = User.objects.create_user(
        settings.TEST_USERNAME,
        settings.TEST_EMAIL,
        settings.TEST_PASSWORD,
        id = settings.TEST_USER_ID,
    )
    # add to admissions sms group
    ag = Group.objects.create(name=settings.TWILIO_ADMISSIONS_GROUP)
    ag.user_set.add(user)
    # profile
    user.sender.phone = settings.TWILIO_TEST_PHONE_FROM
    user.sender.message_sid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID
    # profile account
    user.sender.account = Account.objects.get(department='Admissions')
    user.sender.save()
    user.save()

    return user
