from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from djtwilio.apps.sms.forms import SendForm

from djtools.utils.logging import seperator

from unittest import skip


@skip("skip for now until we can figure out a way to fake a request w/ a user")
class SendFormTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        request = self.factory.get(reverse('sms_send_form'))

    def test_send_form_valid_data(self):
        form = SendForm({
            'phone_to': settings.TWILIO_TEST_PHONE_TO,
            'message': settings.TWILIO_TEST_MESSAGE
        })
        self.assertTrue(form.is_valid())

    def test_send_form_invalid_data(self):
        form = SendForm({
            'phone_to': '8675309',
            'message': '',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'phone_to': ['Phone numbers must be in XXX-XXX-XXXX format.'],
            'message': ['This field is required.'],
        })

    def test_send_form_opt_out_data(self):
        form = SendForm({
            'phone_to': settings.TWILIO_TEST_PHONE_OPT_OUT,
            'message': settings.TWILIO_TEST_MESSAGE
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'phone_to': ['This student has chosen to opt-out of phone contact.'],
        })

    def test_send_form_blank_data(self):
        form = SendForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'phone_to': ['This field is required.'],
            'message': ['This field is required.'],
        })
