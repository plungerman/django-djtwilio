# -*- coding: utf-8 -*-

import csv
import json
import logging
import re
import unicodedata

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from djtools.utils.mail import send_mail
from djtools.utils.cypher import AESCipher
from djtwilio.apps.sms.data import CtcBlob
from djtwilio.apps.sms.forms import BulkForm
from djtwilio.apps.sms.forms import DocumentForm
from djtwilio.apps.sms.forms import IndiForm
from djtwilio.apps.sms.forms import StatusCallbackForm
from djtwilio.apps.sms.models import Bulk
from djtwilio.apps.sms.models import Error
from djtwilio.apps.sms.models import Message
from djtwilio.apps.sms.models import Status
from djtwilio.apps.sms.errors import MESSAGE_DELIVERY_CODES
from djtwilio.core.models import Account
from djtwilio.core.models import Sender
from djtwilio.core.utils import send_message
from djzbar.utils.informix import get_session
from djzbar.decorators.auth import portal_auth_required

from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse, Say


logger = logging.getLogger(__name__)
EARL = settings.INFORMIX_EARL


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
        objects = Message.objects.filter(bulk=bulk)
        response = render(
            request,
            'apps/sms/bulk_detail.html',
            {'bulk':bulk, 'objects': objects},
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
            for m in sender.messenger.all().order_by('-date_created'):
                messages.append(m)
    return render(
        request, 'apps/sms/individual_list.html', {'messages': messages},
    )


@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def detail(request, sid, medium='screen'):
    """Display the details of a message."""
    user = request.user
    try:
        message = Message.objects.get(status__MessageSid=sid)
    except:
        raise Http404
    template = 'apps/sms/detail_{}.html'.format(medium)
    if message.messenger.user != user and not user.is_superuser:
        response = HttpResponseRedirect(
            reverse('sms_send_form')
        )
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
            for m in sender.messenger.all().order_by('-date_created')[:limit]:
                messages.append(m)
    return render(
        request, 'apps/sms/home.html', {'messages': messages,'bulk':bulk},
    )


@csrf_exempt
@portal_auth_required(
    session_var='DJTWILIO_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def get_sender(request):
    """Return a message in json format from a POST request."""
    results = {'sender': '', 'student_number': '', 'message': ""}
    if request.method=='POST':
        phone = request.POST.get('phone_to')
        if phone:
            sids = []
            for s in request.user.sender.all():
                sids.append(s.id)
            messages = Message.objects.filter(recipient=phone).filter(
                messenger__id__in=sids
            ).order_by('-date_created')
            if messages:
                message = messages[0]
                results['sender'] = '{}'.format(message.messenger.id)
                results['student_number'] = '{}'.format(
                    message.student_number
                )
                msg = "Success"
            else:
                msg = "No phone number provided."
        else:
            msg = "No phone number provided."
    else:
        # requires POST
        msg = "Method must be POST."
    results['message'] = msg
    return HttpResponse(
        json.dumps(results), content_type='application/json; charset=utf-8',
    )


@csrf_exempt
def status_callback(request, mid=None):
    """Handle the callback requests from the twilio API."""
    # see: https://www.twilio.com/docs/sms/twiml#request-parameters
    content_type='text/plain; charset=utf-8'
    if request.method=='POST':
        post = request.POST
        if settings.DEBUG:
            for k,v in post.items():
                logger.debug(u'{0}: {1}'.format(k,v))
        # if we do not have an Account ID, it is not a legitimate request sent
        # from twilio and there is no need to go further
        account = get_object_or_404(Account, sid=post['AccountSid'])
        msg = ""
        # message status for form instance
        status = None
        if mid:
            cipher = AESCipher(bs=16)
            mid = cipher.decrypt(mid)
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
                content_type='text/xml; charset=utf-8'
                try:
                    sender = Sender.objects.get(phone=status.To[2:])
                    phone = sender.forward_phone
                except:
                    phone = settings.TWILIO_DEFAULT_FORWARD_PHONE
                msg.dial(phone)
                logger.debug('forwarding = {0}'.format(msg))
            else:
                # callback from the API when recipient has replied to an SMS
                if not mid:
                    # remove extraneous characters and country code for US
                    frum = str(status.From).translate(None, '.+()- ')[1:]
                    recipient = str(status.To).translate(None, '.+()- ')
                    # obtain message from our sender
                    m = Message.objects.filter(recipient=frum).order_by(
                        '-date_created',
                    ).first()
                    sender = m.messenger
                    message = Message(
                        messenger=sender,
                        recipient=recipient,
                        student_number=m.student_number,
                        body=status.Body,
                        status=status,
                    )
                    message.save()
                    to = None
                    email_to = [sender.user.email]
                    if settings.DEBUG:
                        to = sender.user.email
                        email_to = [settings.MANAGERS[0][1]]
                    subject = "[DJ Twilio] reply from one your contacts"
                    data = {
                        'status': status,
                        'original': m,
                        'response': message,
                        'to':to,
                    }
                    send_mail(
                        request,
                        email_to,
                        subject,
                        settings.DEFAULT_FROM_EMAIL,
                        'apps/sms/reply_email.html',
                        data,
                        [settings.MANAGERS[0][1]],
                    )
                    status.MessageStatus = 'received'
                    message.status = status
                    status.save()
                # update informix
                if status.MessageStatus in ['delivered','received']:
                    # create the ctc_blob object with the value of
                    # the message body for txt
                    session = get_session(EARL)
                    # informix does not like unicode for their blob and
                    # it has to be a string, so here we deal with
                    # non-standar characters that do not work with
                    # python strings
                    body = unicodedata.normalize(
                        'NFKD', message.body
                    ).encode('ascii','ignore')
                    blob = CtcBlob(txt=body)
                    session.add(blob)
                    session.flush()
                    # insert into database
                    text_type = 'TEXTOUT'
                    if message.bulk:
                        text_type = 'TEXTMASS'
                    stat = 'C'
                    if status.MessageStatus == 'received':
                        text_type = 'TEXTIN'
                        stat = 'E'
                    sql = '''
                        INSERT INTO ctc_rec (
                            id, tick, add_date, due_date, cmpl_date,
                            resrc, bctc_no, stat
                        )
                        VALUES (
                            {},"ADM",TODAY,TODAY,TODAY,"{}",{},"{}"
                        )
                    '''.format(
                        message.student_number, text_type, blob.bctc_no, stat
                    )
                    session.execute(sql)
                    session.commit()
                    session.close()
                    if not msg:
                        if settings.DEBUG:
                            msg = status.MessageStatus
                        else:
                            logger.debug("msg = Success")
        else:
            msg = "Invalid POST data"
    else:
        msg = "Requires POST"
        if settings.DEBUG:
            logger.debug("msg = {}".format(msg))

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

    if request.method=='POST':
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
                data = form_bulk.cleaned_data
                bulk = form_bulk.save()
                rep = 'rep_first'
                indx = None
                # firstname, lastname, phone, cid, rep_first
                with open(bulk.distribution.path, 'rb') as csvfile:
                    # read 1MB chunks to ensure the sniffer works for files
                    # of any size without running out of memory:
                    dialect = csv.Sniffer().sniff(csvfile.read(1024*1024))
                    csvfile.seek(0)
                    delimiter = dialect.delimiter
                    reader = csv.reader(
                        csvfile, delimiter=delimiter, quoting=csv.QUOTE_NONE,
                    )
                    for row in reader:
                        if rep in row:
                            indx = row.index(rep)
                            # skip header row
                        else:
                            body = data['message']
                            if indx:
                                body = body.replace(rep, row[indx])
                            sent = send_message(
                                Client(
                                    bulk.sender.account.sid,
                                    bulk.sender.account.token,
                                ),
                                bulk.sender,
                                row[2],             # recipient
                                body,               # body
                                row[3],             # cid
                                bulk=bulk,
                                doc=phile,
                            )
                messages.add_message(
                    request, messages.SUCCESS, """
                        Your messages have been sent. View the
                        <a href="{}" class="message-status text-primary">
                        delivery report</a>.
                    """.format(reverse('sms_bulk_detail', args=[bulk.id])),
                    extra_tags='alert alert-success'
                )
                response = HttpResponseRedirect( reverse('sms_send_form') )
        else:  # single recipient message, not bulk
            if form_indi.is_valid() and form_doc.is_valid():
                data = form_indi.cleaned_data
                doc = form_doc.cleaned_data
                if doc['phile']:
                    phile = form_doc.save(commit=False)
                    phile.created_by = user
                    phile.updated_by = user
                    phile.save()
                sender = Sender.objects.get(pk=data['phone_from'])
                body = data['message']
                recipient = data['phone_to']
                sent = send_message(
                    Client(sender.account.sid, sender.account.token),
                    sender,
                    recipient,
                    body,
                    data.get('student_number'),
                    doc=phile,
                )
                if sent['message']:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
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
                                    ]
                                )
                            ),
                        extra_tags='alert alert-success',
                    )
                else:  # message fail
                    messages.add_message(
                        request,
                        messages.ERROR,
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
                'form_doc':form_doc,
            }
        )

    return response
