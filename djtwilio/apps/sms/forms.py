# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from djtwilio.core.models import Sender
from djtwilio.apps.sms.models import Bulk, Document, Status
from djtwilio.apps.sms.models import Bulk, Status

from djtools.fields.localflavor import USPhoneNumberField
from djzbar.utils.informix import do_sql

DEBUG = settings.INFORMIX_DEBUG


class StatusCallbackForm(forms.ModelForm):
    """
    POST:
    {
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
    }


    """

    class Meta:
        model = Status
        fields = '__all__'


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['phile',]


class BulkForm(forms.ModelForm):

    #sender = forms.CharField()
    message = forms.CharField(
        label = "Message to Recipients",
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text = '<span id="bulk-chars">160</span> characters remaining'
    )

    class Meta:
        model = Bulk
        fields = ['name','description','distribution','sender',]


class IndiForm(forms.Form):

    phone_to = USPhoneNumberField(
        label = "To",
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'required form-control'}),
    )
    student_number = forms.CharField(
        label = "Student ID",
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'required form-control'}),
    )
    phone_from = forms.CharField()
    message = forms.CharField(
        label = "Message to Recipient",
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text = '<span id="indi-chars">160</span> characters remaining'
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user = self.request.user
        super(IndiForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            senders = Sender.objects.all().order_by('-alias')
        else:
            senders = user.sender.all().order_by('-alias')

        choices = [("","---Phone or Messaging Service---")]
        for s in senders:
            phone = s.phone
            if not phone:
                phone = ''
            choices.append((s.id, "{} {}".format(phone, s.alias)))

        self.fields['phone_from'] = forms.ChoiceField(
            label = "From", choices=choices,
            widget=forms.Select(attrs={'class': 'required form-control'})
        )

    def clean(self):
        """
        opt_out = "Y" should mean "do not send text".
        """

        opt_out = False
        cd = self.cleaned_data
        phone = cd.get('phone_to')
        sql = 'SELECT * FROM aa_rec WHERE phone="{}"'.format(phone)
        objects = do_sql(sql, key=DEBUG)
        for o in objects:
            sid = o.id
            if o.opt_out == 'Y':
                opt_out = True

        if opt_out:
            self._errors['phone_to'] = self.error_class(
                ["This student has chosen to opt-out of phone contact."]
            )
        #else:
            #if not self.cleaned_data.get('student_number'):
                #self.cleaned_data['student_number'] = sid

        return cd
