from django.conf.urls import url
from django.views.generic import TemplateView

from djtwilio.apps.sms import views


urlpatterns = [
    url(
        r'^send/$',
        views.send_form, name='sms_send_form'
    ),
    url(
        r'^send/success/$',
        TemplateView.as_view(
            template_name='core/admissions/sms/success.html'
        ),
        name='sms_send_form_success'
    ),
    url(
        r'^status-callback/$',
        views.status_callback, name='sms_status_callback'
    ),
    url(
        r'^detail/(?P<sid>\w+)/(?P<medium>[-\w]+)/$',
        views.detail, name='sms_detail'
    ),
    url(
        r'^detail/(?P<sid>\w+)/$',
        views.detail, name='sms_detail_default'
    ),
    url(
        r'^get-sender/$',
        views.get_sender, name='get_sender'
    ),
    url(
        r'^list/$',
        views.list, name='sms_list'
    ),
    url(
        r'^search/$',
        views.search, name='sms_search'
    ),
]
