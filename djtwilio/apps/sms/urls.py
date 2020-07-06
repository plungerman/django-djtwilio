from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from djtwilio.apps.sms import views


urlpatterns = [
    url(
        r'^send/$', views.send_form, name='sms_send_form'
    ),
    url(
        r'^send/success/$',
        TemplateView.as_view(
            template_name='core/admissions/sms/success.html'
        ),
        name='sms_send_form_success'
    ),
    # response from API when recipient replies to an SMS
    url(
        r'^callback/reply/$',
        views.status_callback, name='sms_reply_callback'
    ),
    # response from API with our Message() object ID encrypted in URL
    url(
        r'^callback/(?P<mid>(.*))/status/$',
        views.status_callback, name='sms_status_callback'
    ),
    url(
        r'^detail/(?P<sid>(.*))/(?P<medium>[-\w]+)/$',
        views.detail, name='sms_detail'
    ),
    url(
        r'^detail/(?P<sid>(.*))/$',
        views.detail, name='sms_detail_default'
    ),
    url(
        r'^bulk/list/$', views.bulk_list, name='sms_bulk_list'
    ),
    url(
        r'^bulk/(?P<bid>\w+)/detail/$',
        views.bulk_detail, name='sms_bulk_detail'
    ),
    url(
        r'^get-sender/$', views.get_sender, name='sms_get_sender'
    ),
    url(
        r'^list/$',
        views.individual_list, name='sms_individual_list'
    ),
    url(
        r'^$', views.home, name='sms_home'
    )
]
