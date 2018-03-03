from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djtwilio.apps.sms.forms import SendForm
from djtwilio.apps.sms.manager import Message
from djtwilio.core.client import twilio_client
from djtwilio.core.models import Account

from djzbar.decorators.auth import portal_auth_required

from twilio.base.exceptions import TwilioRestException

MESSAGING_SERVICE_SID = settings.TWILIO_TEST_MESSAGING_SERVICE_SID


@portal_auth_required(
    #group='Admissions SMS', session_var='DJTWILIO_AUTH',
    session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
@csrf_exempt
def send(request):

    initial = {}

    if request.method=='POST':
        form = SendForm(request.POST, request.FILES)
        user = request.user
        account = user.profile.account
        if form.is_valid():
            data = form.cleaned_data

            die = False
            client = twilio_client(account)
            try:
                response = client.messages.create(
                    to = data['phone_to'],
                    messaging_service_sid = account.sid,
                    # use parentheses to prevent extra whitespace
                    body = (data['message']),
                    status_callback = 'https://requestb.in/19mnap81'
                )
            except TwilioRestException as e:
                die = True
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='error'
                )

            if not die:
                message = Message().status(response.sid, 'delivered')

                if message.status == 'delivered':
                    messages.add_message(
                        request,messages.SUCCESS,"Your message has been sent.",
                        extra_tags='success'
                    )
                else:
                    messages.add_message(
                        request, messages.ERROR, "{}: {}".format(
                            message.error_message,
                            MESSAGE_DELIVERY[message.error_code]
                        )
                    )

            return HttpResponseRedirect(
                reverse_lazy('sms_send')
            )

    else:
        if settings.DEBUG:
            initial = {
                'phone_to': settings.TWILIO_TEST_PHONE_TO,
                'message': settings.TWILIO_TEST_MESSAGE
            }
        form = SendForm(initial=initial)

    return render(
        request, 'apps/sms/form.html', {'form': form}
    )


def send_bulk(request):
    return render(
        request, 'apps/sms/form_bulk.html'
    )


def detail(request, sid):
    return render(
        request, 'apps/sms/detail.html'
    )


def search(request):
    return render(
        request, 'apps/sms/search.html'
    )
