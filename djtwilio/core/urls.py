# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from djtwilio.core import views
from djauth.views import loggedout


admin.autodiscover()
admin.site.site_header = 'Carthage College'

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'


urlpatterns = [
    # django admin and loginas
    url(r'^rocinante/', include(admin.site.urls)),
    url(r'^rocinante/', include('loginas.urls')),
    # admin honeypot
    url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # auth
    url(
        r'^accounts/login/$',
        auth_views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login',
    ),
    url(
        r'^accounts/logout/$',
        auth_views.logout,
        {'next_page': reverse_lazy('auth_loggedout')},
        name='auth_logout',
    ),
    url(
        r'^accounts/loggedout/$',
        loggedout,
        {'template_name': 'accounts/logged_out.html'},
        name='auth_loggedout',
    ),
    url(
        r'^accounts/profile/sender/manager/$',
        views.sender_manager,
        name='sender_manager',
    ),
    url(
        r'^accounts/profile/sender/manager/(?P<sid>\w+)/(?P<action>[-\w]+)/$',
        views.sender_manager,
        name='sender_update',
    ),
    url(r'^accounts/profile/$', views.user_profile, name='user_profile'),
    url(r'^accounts/$', RedirectView.as_view(url=reverse_lazy('auth_login'))),
    url(
        r'^denied/$',
        TemplateView.as_view(
            template_name='denied.html'
        ),
        name='access_denied',
    ),
    url(r'^core/student/list/$', views.student_list, name='student_list'),
    # apps could have its own urls.py file eventually
    url(r'^sms/', include('djtwilio.apps.sms.urls')),
    # redirect home request to sms for now
    url(r'^$', RedirectView.as_view(url=reverse_lazy('sms_send_form'))),
]
urlpatterns += url("admin/", include('loginas.urls')),
