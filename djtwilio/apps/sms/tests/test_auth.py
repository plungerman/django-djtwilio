from django.contrib.auth.models import Group, User
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from djtools.utils.logging import seperator

from djzbar.utils.informix import get_session

from unittest import skip


@skip("skip for now until bulk test if built")
class AppsSmsAuthTestCase(TestCase):

    fixtures = [ 'user.json','profile','sender.json','account.json' ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)
        self.password = settings.TEST_PASSWORD
        self.user.set_password(self.password)
        self.user.save()

    def test_auth(self):
        print("\n")
        print("Test Auth")
        seperator()
        print("earl:")
        earl = reverse('sms_send_form')
        print(earl)
        # get SMS send page
        response = self.client.get(earl)
        self.assertEqual(response.status_code, 302)
        # redirect to sign in page
        print("redirect to sign in at {}".format(response['location']))

        # attempt to sign in with client login method
        login = self.client.login(
            username=self.user.username, password=self.password
        )
        self.assertTrue(login)
        response = self.client.get(earl)
        self.assertEqual(response.status_code, 200)
        print("URL:")
        print(response.request['PATH_INFO'])
        print("Auth Success")
