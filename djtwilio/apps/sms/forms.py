# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from djtwilio.core.models import Sender
from djtwilio.apps.sms.models import Bulk, Status

from djzbar.utils.informix import do_sql

from localflavor.us.forms import USPhoneNumberField

DEBUG = settings.INFORMIX_DEBUG


class StatusCallbackForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = '__all__'


class BulkForm(forms.ModelForm):

    messaging_service = forms.CharField()
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text = '<span id="bulk-chars">160</span> characters remaining'
    )

    class Meta:
        model = Bulk
        fields = ['name','description','distribution']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        user = request.user
        super(BulkForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            senders = Sender.objects.filter(messaging_service_sid__isnull=False)
        else:
            senders = user.sender.filter(messaging_service_sid__isnull=False)

        choices = [("","---Messaging Service SID---")]
        for s in senders:
            choices.append(
                (s.id, "{} ({})".format(s.nickname, s.messaging_service_sid))
            )

        self.fields['messaging_service'] = forms.ChoiceField(
            label = "Messaging Service", choices=choices,
            widget=forms.Select(attrs={'class': 'required form-control'})
        )


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
        widget=forms.Textarea(attrs={'class': 'required form-control'}),
        help_text = '<span id="indi-chars">160</span> characters remaining'
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user = self.request.user
        super(IndiForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            senders = Sender.objects.all()
        else:
            senders = user.sender.all()

        choices = [("","---Phone number---")]
        for s in senders:
            choices.append((s.id, "{} ({})".format(s.phone, s.nickname)))

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
