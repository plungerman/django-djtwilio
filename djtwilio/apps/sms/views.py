# -*- coding: utf-8 -*-

import datetime
import json
import logging
import re
import unicodedata

from django.conf import settings
from django.contrib import messages as djmessages
from django.db import connections
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_q.models import Schedule
from djauth.decorators import portal_auth_required
from djimix.core.encryption import decrypt
from djtools.utils.mail import send_mail
from twilio.twiml.voice_response import VoiceResponse

from djtwilio.apps.sms.forms import BulkForm
from djtwilio.apps.sms.forms import DocumentForm
from djtwilio.apps.sms.forms import IndiForm
from djtwilio.apps.sms.forms import StatusCallbackForm
from djtwilio.apps.sms.models import Bulk
from djtwilio.apps.sms.models import Error
from djtwilio.apps.sms.models import Message
from djtwilio.core.data import CtcBlob
from djtwilio.core.models import Account
from djtwilio.core.models import Sender
from djtwilio.core.utils import send_message


logger = logging.getLogger(__name__)


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def bulk_detail(request, bid):
    """View the details of a bulk message."""
    user = request.user
    bulk = get_object_or_404(Bulk, pk=bid)
    if bulk.sender.user != user and not user.is_superuser:
        response = HttpResponseRedirect(reverse('sms_send_form'))
    else:
        messages = Message.objects.filter(bulk=bulk)
        response = render(
            request,
            'apps/sms/bulk_detail.html',
            {'bulk': bulk, 'objects': messages},
        )

    return response


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def bulk_list(request):
    """Display all bulk messages for a user or all for superusers."""
    user = request.user
    if user.is_superuser:
        bulk = Bulk.objects.all().order_by('-date_created')
    else:
        bulk = Bulk.objects.filter(sender=user).order_by('-date_created')
    return render(request, 'apps/sms/bulk_list.html', {'bulk': bulk})


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def individual_list(request):
    """Display all single recipient messages for a use all for superusers."""
    user = request.user
    if user.is_superuser:
        messages = Message.objects.all().order_by('-date_created')
    else:
        messages = []
        for sender in user.sender.all():
            for message in sender.messenger.all().order_by('-date_created'):
                messages.append(message)
    return render(
        request, 'apps/sms/individual_list.html', {'messages': messages},
    )


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def detail(request, sid, medium='screen'):
    """Display the details of a message."""
    user = request.user
    message = get_object_or_404(Message, status__MessageSid=sid)
    template = 'apps/sms/detail_{0}.html'.format(medium)
    if message.messenger.user != user and not user.is_superuser:
        response = HttpResponseRedirect(reverse('sms_send_form'))
    else:
        response = render(request, template, {'message': message})
    return response


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """Display the first 100 messages for a user."""
    limit = 100
    user = request.user
    if user.is_superuser:
        bulk = Bulk.objects.all().order_by('-date_created')[:limit]
        messages = Message.objects.all().order_by('-date_created')[:limit]
    else:
        bulk = Bulk.objects.filter(sender__user=request.user).order_by(
            '-date_created',
        )[:limit]
        messages = []
        limit = limit / user.sender.count()
        for sender in user.sender.all():
            for mes in sender.messenger.all().order_by('-date_created')[:limit]:
                messages.append(mes)
    return render(
        request, 'apps/sms/home.html', {'messages': messages, 'bulk': bulk},
    )


@csrf_exempt
@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def get_sender(request):
    """Return a message in json format from a POST request."""
    sender_dict = {'sender': '', 'student_number': '', 'message': ""}
    if request.method == 'POST':
        phone = request.POST.get('phone_to')
        if phone:
            sids = []
            for sender in request.user.sender.all():
                sids.append(sender.id)
            messages = Message.objects.filter(recipient=phone).filter(
                messenger__id__in=sids,
            ).order_by('-date_created')
            if messages:
                message = messages[0]
                sender_dict['sender'] = str(message.messenger.id)
                sender_dict['student_number'] = str(message.student_number)
                msg = "Success"
            else:
                msg = "No phone number provided."
        else:
            msg = "No phone number provided."
    else:
        # requires POST
        msg = "Method must be POST."
    sender_dict['message'] = msg
    return HttpResponse(
        json.dumps(sender_dict), content_type='application/json; charset=utf-8',
    )


@csrf_exempt
def status_callback(request, mid=None):
    """Handle the callback requests from the twilio API."""
    # see: https://www.twilio.com/docs/sms/twiml#request-parameters
    content_type = 'text/plain; charset=utf-8'
    if request.method == 'POST':
        post = request.POST
        if settings.DEBUG:
            for key, datum in post.items():
                logger.debug('{0}: {1}'.format(key, datum))
        # if we do not have an Account ID, it is not a legitimate request sent
        # from twilio and there is no need to go further
        get_object_or_404(Account, sid=post['AccountSid'])
        msg = ""
        # message status for form instance
        status = None
        message = None
        if mid:
            mid = decrypt(mid)
            message = Message.objects.get(pk=mid)
            status = message.status
        form = StatusCallbackForm(post, instance=status)
        if form.is_valid():
            status = form.save(commit=False)
            if status.ErrorCode:
                error = Error.objects.filter(code=status.ErrorCode).first()
                status.error = error
            status.save()
            # callback from the API when someone makes a voice call
            # to a phone number
            if status.CallSid:
                msg = VoiceResponse()
                content_type = 'text/xml; charset=utf-8'
                try:
                    sender = Sender.objects.get(phone=status.To[2:])
                except Exception:
                    sender = None
                if sender:
                    phone = sender.forward_phone
                else:
                    phone = settings.TWILIO_DEFAULT_FORWARD_PHONE
                msg.dial(phone)
                logger.debug('forwarding = {0}'.format(msg))
            else:
                # callback from the API when recipient has replied to an SMS
                if not mid:
                    # remove extraneous characters and country code for US (1)
                    frum = re.sub('[^A-Za-z0-9]+', '', status.From)[1:]
                    recipient = re.sub('[^A-Za-z0-9]+', '', status.To)
                    # obtain message from our sender
                    mess_orig = Message.objects.filter(recipient=frum).order_by(
                        '-date_created',
                    ).first()
                    to = None
                    if mess_orig:
                        sender = mess_orig.messenger
                        message = Message(
                            messenger=sender,
                            recipient=recipient,
                            student_number=mess_orig.student_number,
                            body=status.Body,
                            status=status,
                        )
                        message.save()
                        body = message.body
                        email_to = [sender.user.email]
                        if settings.DEBUG:
                            to = sender.user.email
                            email_to = [settings.MANAGERS[0][1]]
                        status.MessageStatus = 'received'
                        message.status = status
                        status.save()
                    else:
                        body = status.Body
                        email_to = [settings.MANAGERS[0][1]]
                    context_dict = {
                        'status': status,
                        'original': mess_orig,
                        'response': message,
                        'to': to,
                        'body': body,
                    }
                    subject = "[DJ Twilio] reply from one your contacts"
                    send_mail(
                        request,
                        email_to,
                        subject,
                        settings.DEFAULT_FROM_EMAIL,
                        'apps/sms/reply_email.html',
                        context_dict,
                        [settings.MANAGERS[0][1]],
                    )
                    # update informix
                    status_list = ['delivered', 'received', 'sent', 'accepted']
                    if status.SmsStatus in status_list:
                        # create the ctc_blob object with the value of
                        # the message body for txt.
                        # informix does not like unicode for their blob and
                        # it has to be a string, so here we deal with
                        # non-standard characters that do not work with
                        # python strings
                        body = unicodedata.normalize(
                            'NFKD', body,
                        ).encode('ascii', 'ignore')
                        blob = CtcBlob.objects.using('informix').create(txt=body)
                        # insert into database
                        text_type = 'TEXTOUT'
                        if message.bulk:
                            text_type = 'TEXTMASS'
                        stat = 'C'
                        if status.MessageStatus == 'received':
                            text_type = 'TEXTIN'
                            stat = 'E'
                        sql = """
                            INSERT INTO ctc_rec (
                                id, tick, add_date, due_date, cmpl_date,
                                resrc, bctc_no, stat
                            )
                            VALUES (
                                {0},"ADM",TODAY,TODAY,TODAY,"{1}",{2},"{3}"
                            )
                        """.format(
                            message.student_number,
                            text_type,
                            blob.bctc_no,
                            stat,
                        )
                        with connections['informix'].cursor() as cursor:
                            cursor.execute(sql)
            if not msg:
                if settings.DEBUG:
                    msg = status.MessageStatus
                else:
                    msg = 'Success'
        else:
            msg = "Invalid POST data"
    else:
        msg = "Requires POST: {0}".format(request.GET)
        logger.debug("msg = {0}".format(msg))

    return HttpResponse(msg, content_type=content_type)


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
@csrf_exempt
def send_form(request):
    """Send a message to the twilio API."""
    bulk = False
    response = False
    template = 'apps/sms/form.html'
    user = request.user

    if request.method == 'POST':
        form_doc = DocumentForm(
            request.POST,
            request.FILES,
            prefix='doc',
            use_required_attribute=False,
        )
        form_bulk = BulkForm(
            request.POST,
            request.FILES,
            prefix='bulk',
            use_required_attribute=False,
        )
        form_indi = IndiForm(
            request.POST,
            request.FILES,
            request=request,
            prefix='indi',
            use_required_attribute=False,
        )
        if user.is_superuser:
            sids = Sender.objects.filter(messaging_service_sid__isnull=False)
        else:
            sids = user.sender.filter(messaging_service_sid__isnull=False)
        form_bulk.fields['sender'].queryset = sids
        phile = None
        # bulk messaging
        if request.POST.get('bulk-submit'):
            bulk = True
            if form_bulk.is_valid() and form_doc.is_valid():
                doc = form_doc.cleaned_data
                if doc['phile']:
                    phile = form_doc.save(commit=False)
                    phile.created_by = user
                    phile.updated_by = user
                    phile.save()
                bulk_clean = form_bulk.cleaned_data
                body = bulk_clean['message']
                bulk = form_bulk.save()
                if bulk_clean['execute_date']:
                    date_string = '{0} {1}'.format(
                        bulk_clean['execute_date'],
                        bulk_clean['execute_time'],
                    )
                    next_run = datetime.datetime.strptime(
                        date_string, '%Y-%m-%d %H:%M:%S',
                    )
                    mensaje = """
                        Your messages have been scheduled for delivery: {0}.
                        View the
                        <a href="{1}" class="message-status text-primary">
                          delivery report</a>.
                    """.format(date_string, reverse('sms_bulk_detail', args=[bulk.id]))
                else:
                    next_run = timezone.now() + datetime.timedelta(minutes=1)
                    mensaje = """
                      Your messages have been sent. View the
                      <a href="{0}" class="message-status text-primary">
                        delivery report</a>.
S>                    """.format(reverse('sms_bulk_detail', args=[bulk.id]))

                pid = None
                if phile:
                    pid = phile.id
                Schedule.objects.create(
                    func='djtwilio.core.utils.send_bulk',
                    args=(bulk.id, body, pid),
                    schedule_type=Schedule.ONCE,
                    next_run=next_run,
                    repeats=1,
                    name='{0}: {1}'.format(bulk.name, next_run),
                )

                djmessages.add_message(
                    request,
                    djmessages.SUCCESS,
                    mensaje,
                    extra_tags='alert alert-success',
                )
                response = HttpResponseRedirect(reverse('sms_send_form'))
        else:  # single recipient message, not bulk
            if form_indi.is_valid() and form_doc.is_valid():
                indi = form_indi.cleaned_data
                doc = form_doc.cleaned_data
                if doc['phile']:
                    phile = form_doc.save(commit=False)
                    phile.created_by = user
                    phile.updated_by = user
                    phile.save()
                sender = Sender.objects.get(pk=indi['phone_from'])
                body = indi['message']
                recipient = indi['phone_to']
                sent = send_message(
                    sender.id,
                    recipient,
                    body,
                    indi.get('student_number'),
                    doc=phile,
                )
                if sent['message']:
                    djmessages.add_message(
                        request,
                        djmessages.SUCCESS,
                        """
                        Your message has been sent. View the
                        <a data-target="#messageStatus" data-toggle="modal"
                        data-load-url="{0}" class="message-status text-primary">
                        message status</a>.
                        """.format(
                            reverse(
                                'sms_detail',
                                args=[
                                    sent['message'].status.MessageSid,
                                    'modal',
                                ],
                            ),
                        ),
                        extra_tags='alert alert-success',
                    )
                else:  # message fail
                    djmessages.add_message(
                        request,
                        djmessages.ERROR,
                        sent['response'],
                        extra_tags='alert alert-danger',
                    )
                response = HttpResponseRedirect(reverse('sms_send_form'))
    else:
        form_doc = DocumentForm(prefix='doc', use_required_attribute=False)
        form_bulk = BulkForm(prefix='bulk', use_required_attribute=False)
        form_indi = IndiForm(
            prefix='indi', request=request, use_required_attribute=False,
        )
        if user.is_superuser:
            sids = Sender.objects.filter(messaging_service_sid__isnull=False)
        else:
            sids = user.sender.filter(messaging_service_sid__isnull=False)
        form_bulk.fields['sender'].queryset = sids

    if not response:
        response = render(
            request, template, {
                'form_indi': form_indi,
                'form_bulk': form_bulk,
                'bulk': bulk,
                'form_doc': form_doc,
            },
        )

    return response
