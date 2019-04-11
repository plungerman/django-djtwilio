from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy

from djtwilio.core.forms import SenderForm, StudentNumberForm
from djtwilio.core.models import Sender
from djtwilio.core.sql import SEARCH_ID, STUDENTS

from djzbar.utils.informix import do_sql
from djzbar.decorators.auth import portal_auth_required


@portal_auth_required(
    group=settings.TWILIO_GROUP, session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def student_list(request):

    students = do_sql(
        STUDENTS(year = '2019', term = 'RC')
    )

    return render(
        request, 'core/student_list.html', {'students':students,}
    )


@portal_auth_required(
    group=settings.TWILIO_GROUP, session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def search(request):

    if request.method=='POST':
        form = StudentNumberForm(request.POST)
        user = request.user
        if form.is_valid():
            data = form.cleaned_data
            students = do_sql(
                SEARCH_ID(student_number = data['student_number'])
            )
    else:
        form = StudentNumberForm()

    return render(
        request, 'core/search.html', {'form': form, 'students':students}
    )


@portal_auth_required(
    group=settings.TWILIO_GROUP, session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def sender_manager(request, sid=None, action=None):

    sender = None
    if sid:
        sender = get_object_or_404(Sender, pk=sid)

    if request.method=='POST':
        form = SenderForm(request.POST, instance=sender)
        user = request.user
        if form.is_valid():
            data = form.save(commit=False)
            data.phone = str(data.phone).translate(None, '.+()- ')
            data.user = request.user
            data.save()
            message = "Your new phone has been created."
            if action:
                message = "Your phone has been updated."

            messages.add_message(
                request, messages.SUCCESS, message,
                extra_tags='alert alert-success'
            )

            return HttpResponseRedirect(
                reverse('user_profile')
            )
    else:
        form = SenderForm(instance=sender)

    return render(
        request, 'accounts/sender_manager.html', {'form': form,}
    )


@portal_auth_required(
    group=settings.TWILIO_GROUP, session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def user_profile(request):

    return render(
        request, 'accounts/user_profile.html'
    )
