# -*- coding: utf-8 -*-

from django.urls import path
from django.urls import re_path
from django.views.generic import TemplateView

from djtwilio.apps.sms import views


urlpatterns = [
    path('send/', views.send_form, name='sms_send_form'),
    path(
        'send/success/',
        TemplateView.as_view(template_name='core/admissions/sms/success.html'),
        name='sms_send_form_success',
    ),
    # response from API when recipient replies to an SMS
    path('callback/reply/', views.status_callback, name='sms_reply_callback'),
    # response from API with our Message() object ID encrypted in URL
    path(
        'callback/<str:mid>/status/',
        views.status_callback,
        name='sms_status_callback',
    ),
    re_path(
        r'^detail/(?P<sid>(.*))/(?P<medium>[-\w]+)/$',
        views.detail,
        name='sms_detail',
    ),
    re_path(
        r'^detail/(?P<sid>(.*))/$',
        views.detail,
        name='sms_detail_default',
    ),
    path('bulk/list/', views.bulk_list, name='sms_bulk_list'),
    path('bulk/<int:bid>)/detail/', views.bulk_detail, name='sms_bulk_detail'),
    path('get-sender/', views.get_sender, name='sms_get_sender'),
    path('list/', views.individual_list, name='sms_individual_list'),
    path('', views.home, name='sms_home'),
]
