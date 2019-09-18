from django.conf.urls import url
from .views import twilio_status_callback_view

urlpatterns = [
    url(r'^twilio-status-callback/(?P<message_pk>[0-9a-f-]+)/$', twilio_status_callback_view, name="twilio-status-callback"),
]
