from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djtwilio.apps.sms.forms import SendForm
from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.errors import MESSAGE_DELIVERY_CODES
from djtwilio.core.client import twilio_client

from djzbar.decorators.auth import portal_auth_required

from twilio.base.exceptions import TwilioRestException

MESSAGING_SERVICE_SID = settings.TWILIO_TEST_MESSAGING_SERVICE_SID


@csrf_exempt
def status_callback(request):

    pass


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
@csrf_exempt
def send(request):

    initial = {}

    if request.method=='POST':
        form = SendForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            die = False
            data = form.cleaned_data
            recipient = data['phone_to']
            body = data['message'],
            message = Message.objects.create(
                messenger = user,
                recipient = recipient,
                body = body
            )
            client = twilio_client(user.profile.account)
            try:
                response = client.messages.create(
                    to = recipient,
                    messaging_service_sid = user.profile.message_sid,
                    # use parentheses to prevent extra whitespace
                    body = (body),
                    status_callback = 'https://requestb.in/tcyl20tc'
                )
            except TwilioRestException as e:
                die = True
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='error'
                )

            if not die:
                sid = response.sid
                message.message_status.sid = sid
                ms = message.status()
                if ms.status == 'delivered':
                    messages.add_message(
                        request,messages.SUCCESS,"Your message has been sent.",
                        extra_tags='success'
                    )
                else:
                    error = Error.objects.get(code=ms.error_code)
                    message.message_status.error = error
                    messages.add_message(
                        request, messages.ERROR, "{}: {}".format(
                            error.message, error.description
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
