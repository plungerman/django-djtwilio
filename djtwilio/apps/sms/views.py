from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djtwilio.apps.sms.forms import SendForm, StatusCallbackForm
from djtwilio.apps.sms.models import Error, Message, Status
from djtwilio.apps.sms.errors import MESSAGE_DELIVERY_CODES
from djtwilio.core.client import twilio_client

from djzbar.decorators.auth import portal_auth_required

from twilio.base.exceptions import TwilioRestException

import re

MESSAGING_SERVICE_SID = settings.TWILIO_TEST_MESSAGING_SERVICE_SID


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def detail(request, sid):

    user = request.user
    message = Message.objects.get(status__MessageSid=sid)
    if message.messenger != user and not user.is_superuser:
        response = HttpResponseRedirect(
            reverse_lazy('sms_send')
        )
    else:
        response = render(
        request, 'apps/sms/detail.html', {'message': message,}
    )

    return response


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def list(request):

    user = request.user
    if user.is_superuser:
        messages = Message.objects.all().order_by('date_created')
    else:
        messages = user.message_messenger.all().order_by('-date_created')

    return render(
        request, 'apps/sms/list.html', {'objects': messages,}
    )


@csrf_exempt
def status_callback(request):

    if request.method=='POST':
        sid = request.POST.get('MessageSid')
        if re.match("^[A-Za-z0-9]*$", sid):
            status = Status.objects.get(MessageSid=sid)
            if status:
                form = StatusCallbackForm(request.POST, instance=status)
                if form.is_valid():
                    status = form.save(commit=False)
                    if status.ErrorCode:
                        error = Error.objects.get(code=status.ErrorCode)
                        status.error = error
                    status.save()
                    msg = "Success"
                else:
                    msg = "Invalid POST data"
            else:
                msg = "No message mataching Sid"
        else:
            msg = "Invalid message Sid"
    else:
        # requires POST
        msg = "Requires POST"

    return HttpResponse(
        msg, content_type='text/plain; charset=utf-8'
    )


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
@csrf_exempt
def send(request):

    initial = {}
    earl = None
    sid = 0
    if settings.DEBUG:
        initial = {
            'phone_to': settings.TWILIO_TEST_PHONE_TO,
            'message': settings.TWILIO_TEST_MESSAGE
        }

    form = SendForm(initial=initial)
    template = 'apps/sms/form.html'
    response = render(
        request, template, {'form': form}
    )

    if request.method=='POST':
        form = SendForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            die = False
            data = form.cleaned_data
            recipient = data['phone_to']
            body = data['message']
            client = twilio_client(user.profile.account)
            try:
                response = client.messages.create(
                    to = recipient,
                    messaging_service_sid = user.profile.message_sid,
                    # use parentheses to prevent extra whitespace
                    body = (body),
                    status_callback = 'https://{}{}'.format(
                        settings.SERVER_URL,
                        reverse_lazy('sms_status_callback')
                    )
                )
            except TwilioRestException as e:
                die = True
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='error'
                )

                response = HttpResponseRedirect(
                    reverse_lazy('sms_send')
                )

            if not die:
                # create Message object
                message = Message.objects.create(
                    messenger = user,
                    recipient = recipient,
                    body = body
                )
                sid = response.sid
                # create Status object
                status = Status.objects.create(SmsSid=sid, MessageSid=sid)
                message.status = status
                message.save()
                messages.add_message(
                    request, messages.SUCCESS, """
                        Your message has been sent. View the
                        <a data-target="#messageStatus" data-toggle="modal"
                          data-remote="{}">
                          message status</a>.
                    """.format(reverse_lazy('sms_detail', args=[sid])),
                    extra_tags='success'
                )

                response = HttpResponseRedirect(
                    reverse_lazy('sms_send')
                )
        else:
            response = render(
                request, template, {'form': form}
            )

    return response


def send_bulk(request):
    return render(
        request, 'apps/sms/form_bulk.html'
    )


def search(request):
    return render(
        request, 'apps/sms/search.html'
    )
