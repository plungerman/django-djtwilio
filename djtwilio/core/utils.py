from django.conf import settings
from django.contrib.auth.models import Group, User

from djtwilio.core.models import Account, Sender


def create_test_user():

    # create the auth user
    user = User.objects.create_user(
        settings.TEST_USERNAME,
        settings.TEST_EMAIL,
        settings.TEST_PASSWORD,
        id = settings.TEST_USER_ID,
    )
    user.save()
    # add to admissions sms group
    ag = Group.objects.create(name=settings.TWILIO_ADMISSIONS_GROUP)
    ag.user_set.add(user)
    # profile
    sender = Sender(
        user = user,
        phone = settings.TWILIO_TEST_PHONE_FROM,
        messaging_service_sid = settings.TWILIO_TEST_MESSAGING_SERVICE_SID,
        account = Account.objects.get(department='Admissions'),
        nickname = 'Test user\'s phone',
        default = True
    )
    sender.save()

    return user
