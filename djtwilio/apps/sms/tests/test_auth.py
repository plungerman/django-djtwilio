from django.contrib.auth.models import Group, User
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from djtwilio.core.utils import create_test_user

from djtools.utils.logging import seperator

from djzbar.utils.informix import get_session


class CoreViewsTestCase(TestCase):

    fixtures = ['account.json']

    def setUp(self):

        self.user = create_test_user()
        print "created user"
        print self.user.id
        self.password = settings.TEST_PASSWORD

    def test_auth(self):
        print "\n"
        print "Test Auth"
        seperator()
        print "earl:"
        earl = reverse('sms_send')
        print earl
        # get SMS send page
        response = self.client.get(earl)
        self.assertEqual(response.status_code, 302)
        # redirect to sign in page
        print "redirect to sign in at {}".format(response['location'])

        # attempt to sign in with client login method
        login = self.client.login(
            username=self.user.username, password=self.password
        )
        self.assertTrue(login)
        response = self.client.get(earl)
        self.assertEqual(response.status_code, 200)
        print "URL:"
        print response.request['PATH_INFO']
        print "Auth Success"
