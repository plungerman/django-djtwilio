# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings

from djtools.fields.localflavor import USPhoneNumberField
from djtools.fields.time import KungfuTimeField
from djtwilio.apps.sms.models import Bulk
from djtwilio.apps.sms.models import Document
from djtwilio.apps.sms.models import Status
from djtwilio.core.models import Sender

DEBUG = settings.INFORMIX_DEBUG


class StatusCallbackForm(forms.ModelForm):
    """Callback form that handles POST requests from the twilio API.

    POST name/value pairs from the API:

    'Body': [''],
    'MessageSid': [''],
    'FromZip': [''],
    'SmsStatus': [''],
    'SmsMessageSid': [''],
    'AccountSid': [''],
    'MessagingServiceSid': [''],
    'FromCity': [''],
    'ApiVersion': ['2010-04-01'],
    'To': [''],
    'From': [''],
    'NumMedia': [''],
    'ToZip': [''],
    'ToCountry': [''],
    'NumSegments': ['1'],
    'ToState': [''],
    'SmsSid': [''],
    'ToCity': [''],
    'FromState': [''],
    'FromCountry': [''],
    # these are for voice calls
    'CallSid': [''],
    'CallStatus': [''],
    'Direction': [''],
    'ForwardedFrom': [''],
    'CallerName': [''],
    'ParentCallSid': ['']
    """

    class Meta:
        """Information about the form class."""

        model = Status
        fields = '__all__'


class DocumentForm(forms.ModelForm):
    """Form class for the Document data class model."""

    class Meta:
        """Information about the form class."""

        model = Document
        fields = ['phile']


class BulkForm(forms.ModelForm):
    """Form class for the Bulk data class model."""

    execute_date = forms.DateField(
        label="Send date (Optional)",
        required=False,
    )
    execute_time = KungfuTimeField(
        label="Send time (Optional)",
        help_text="(Format HH:MM am/pm)",
        required=False,
    )
    message = forms.CharField(
        label="Message to Recipients",
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text='<span id="bulk-chars">160</span> characters remaining',
    )

    class Meta:
        """Information about the form class."""

        model = Bulk
        fields = ['name', 'description', 'distribution', 'sender']

    def clean(self):
        """Deal with grants officer."""
        cd = self.cleaned_data
        date = cd.get('execute_date')
        time = cd.get('execute_time')
        if date and not time:
            self.add_error('execute_time', "Please provide a time.")
        elif time and not date:
            self.add_error('execute_date', "Please provide a date.")

        return cd


class IndiForm(forms.Form):
    """Form class for sending individual SMS messages."""

    phone_to = USPhoneNumberField(
        label="To",
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'required form-control'}),
    )
    student_number = forms.CharField(
        label="Student ID",
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'required form-control'}),
    )
    phone_from = forms.CharField()
    message = forms.CharField(
        label="Message to Recipient",
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text='<span id="indi-chars">160</span> characters remaining',
    )

    def __init__(self, *args, **kwargs):
        """Override the init method to constructure the sender select field."""
        self.request = kwargs.pop('request', None)
        user = self.request.user
        super(IndiForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            senders = Sender.objects.all().order_by('-alias')
        else:
            senders = user.sender.all().order_by('-alias')

        choices = [("", "---Phone or Messaging Service---")]
        for sender in senders:
            phone = sender.phone
            if not phone:
                phone = ''
            choices.append((sender.id, '{0} {1}'.format(phone, sender.alias)))

        self.fields['phone_from'] = forms.ChoiceField(
            label="From",
            choices=choices,
            widget=forms.Select(attrs={'class': 'required form-control'}),
        )
