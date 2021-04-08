# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from djauth.views import loggedout

from djtwilio.core import views

admin.autodiscover()
admin.site.site_header = 'Carthage College'

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'


urlpatterns = [
    # django admin and loginas
    path('rocinante/', include(admin.site.urls)),
    path('rocinante/', include('loginas.urls')),
    # admin honeypot
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # auth
    path(
        'accounts/login/',
        auth_views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login',
    ),
    path(
        'accounts/logout/',
        auth_views.logout,
        {'next_page': reverse_lazy('auth_loggedout')},
        name='auth_logout',
    ),
    path(
        'accounts/loggedout/',
        loggedout,
        {'template_name': 'accounts/logged_out.html'},
        name='auth_loggedout',
    ),
    path(
        r'^accounts/profile/sender/manager/$',
        views.sender_manager,
        name='sender_manager',
    ),
    path(
        r'^accounts/profile/sender/manager/(?P<sid>\w+)/(?P<action>[-\w]+)/$',
        views.sender_manager,
        name='sender_update',
    ),
    path(r'^accounts/profile/$', views.user_profile, name='user_profile'),
    path(r'^accounts/$', RedirectView.as_view(url=reverse_lazy('auth_login'))),
    path(
        r'^denied/$',
        TemplateView.as_view(
            template_name='denied.html'
        ),
        name='access_denied',
    ),
    path(r'^core/student/list/$', views.student_list, name='student_list'),
    # apps could have its own urls.py file eventually
    path(r'^sms/', include('djtwilio.apps.sms.urls')),
    # redirect home request to sms for now
    path(r'^$', RedirectView.as_view(url=reverse_lazy('sms_send_form'))),
]
