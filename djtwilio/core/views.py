from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy

from djtwilio.core.forms import StudentNumberForm
from djtwilio.core.sql import SEARCH_ID

from djzbar.utils.informix import do_sql
from djzbar.decorators.auth import portal_auth_required


@portal_auth_required(
    group='Admissions SMS', session_var='DJTWILIO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def search(request):

    if request.method=='POST':
        form = StudentNumberForm(request.POST)
        user = request.user
        if form.is_valid():
            data = form.cleaned_data
            sql = SEARCH_ID(student_number = data['student_number']
            students = do_sql(sql)
    else:
        form = StudentNumberForm()

    return render(
        request, 'core/search.html', {'form': form, 'students':students}
    )
