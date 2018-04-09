from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djtwilio.apps.sms.forms import SendForm, StatusCallbackForm
from djtwilio.apps.sms.models import Error, Message, Status
from djtwilio.apps.sms.errors import MESSAGE_DELIVERY_CODES
from djtwilio.core.client import twilio_client

from djzbar.decorators.auth import portal_auth_required

from twilio.base.exceptions import TwilioRestException

import re
import json

MESSAGING_SERVICE_SID = settings.TWILIO_TEST_MESSAGING_SERVICE_SID


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def detail(request, sid, medium='screen'):

    user = request.user

    try:
        message = Message.objects.get(status__MessageSid=sid)
    except:
        raise Http404

    template = 'apps/sms/detail_{}.html'.format(medium)
    if message.messenger.user != user and not user.is_superuser:
        response = HttpResponseRedirect(
            reverse('sms_send')
        )
    else:
        response = render(
        request, template, {'message': message,}
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
        messages = []
        for sender in user.sender.all():
            for m in sender.messenger.all().order_by('-date_created'):
                messages.append(m)

    return render(
        request, 'apps/sms/list.html', {'objects': messages,}
    )


@csrf_exempt
@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def get_messaging_service_sid(request):

    results = {'messaging_service_sid':'','student_number':'','message':""}
    if request.method=='POST':
        phone = request.POST.get('phone_to')
        if phone:
            try:
                message = Message.objects.filter(
                    recipient=phone
                ).order_by('-date_created')[0]
                results['messaging_service_sid'] = '{}'.format(
                    message.messenger.messaging_service_sid
                )
                results['student_number'] = '{}'.format(
                    message.student_number
                )
                msg = "Success"
            except:
                msg = "No messages sent to that phone number."
        else:
            msg = "No phone number provided."
    else:
        # requires POST
        msg = "Method must be POST."

    results['message'] = msg
    return HttpResponse(
        json.dumps(results), content_type='application/json; charset=utf-8'
    )


@csrf_exempt
def status_callback(request):

    if request.method=='POST':
        sid = request.POST.get('MessageSid')
        if re.match("^[A-Za-z0-9]*$", sid):
            status = Status.objects.get(MessageSid=sid)
            if status:
                if status.MessageStatus != 'delivered':
                    form = StatusCallbackForm(request.POST, instance=status)
                    if form.is_valid():
                        status = form.save(commit=False)
                        if status.ErrorCode:
                            error = Error.objects.get(code=status.ErrorCode)
                            status.error = error
                        status.save()
                        # update informix
                        msg = "Success"
                    else:
                        msg = "Invalid POST data"
                else:
                    msg = "MessageStatus has already been set to 'delivered'"
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
            #'phone_to': settings.TWILIO_TEST_PHONE_TO,
            'message': settings.TWILIO_TEST_MESSAGE
        }

    form = SendForm(initial=initial, request=request)
    template = 'apps/sms/form.html'
    response = render(
        request, template, {'form': form}
    )

    if request.method=='POST':
        form = SendForm(request.POST, request=request)
        user = request.user
        if form.is_valid():
            die = False
            data = form.cleaned_data
            messaging_service_sid = data['messaging_service_sid']
            sender = user.sender.get(
                messaging_service_sid = messaging_service_sid
            )
            recipient = data['phone_to']
            body = data['message']
            client = twilio_client(sender.account)
            try:
                response = client.messages.create(
                    to = recipient,
                    messaging_service_sid = messaging_service_sid,
                    # use parentheses to prevent extra whitespace
                    body = (body),
                    status_callback = 'https://{}{}'.format(
                        settings.SERVER_URL,
                        reverse('sms_status_callback')
                    )
                )
            except TwilioRestException as e:
                die = True
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='alert alert-danger'
                )

                response = HttpResponseRedirect(
                    reverse('sms_send')
                )

            if not die:
                # create Message object
                message = Message.objects.create(
                    messenger = sender,
                    recipient = recipient,
                    student_number = data.get('student_number'),
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
                          data-load-url="{}" class="text-primary">
                          message status</a>.
                    """.format(reverse('sms_detail', args=[sid,'modal'])),
                    extra_tags='alert alert-success'
                )

                response = HttpResponseRedirect(
                    reverse('sms_send')
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
