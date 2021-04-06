# -*- coding: utf-8 -*-

from django import forms
from djtwilio.core.models import Account, Sender
from djtools.fields.localflavor import USPhoneNumberField
from localflavor.us.forms import USZipCodeField


class StudentNumberForm(forms.Form):
    """Form class for student ID."""

    student_number = forms.IntegerField(
        label = "Student ID",
        widget=forms.TextInput(attrs={'placeholder': 'Student ID'}),
    )


class SenderForm(forms.ModelForm):
    """Form class for the Sender data model class."""

    phone = USPhoneNumberField(
        label="Phone number",
        required=False,
    )
    forward_phone = USPhoneNumberField(
        label="Forwarding Phone number",
        required=False,
    )
    messaging_service_sid = forms.CharField(
        label="Messaging service ID",
        required=False, max_length = 34,
        help_text="A 34 character code associated with the phone number",
    )
    account = forms.ModelChoiceField(
        label = "Account",
        queryset = Account.objects.all(),
        required = True,
    )
    alias = forms.CharField(label = "Alias", required = True)

    class Meta:
        """Information about the form class."""

        model = Sender
        exclude = ('user',)

    def clean_messaging_service_sid(self):
        """Data validation method for the messaging service ID (SID)."""
        sid = self.cleaned_data.get('messaging_service_sid')
        if sid and len(sid) < 34:
            self._errors['messaging_service_sid'] = self.error_class(
                ["Messaging Services SID is 34 characters."]
            )

        return sid

    def clean(self):
        """Data validation method to determine if a phone or SID is provided."""
        cd = self.cleaned_data
        if not cd.get('phone') and not cd.get('messaging_service_sid'):
            self._errors['messaging_service_sid'] = self.error_class(
                ["Provide either a phone or a service SID."]
            )
            self._errors['phone'] = self.error_class(
                ["Provide either a phone or a service SID."]
            )
