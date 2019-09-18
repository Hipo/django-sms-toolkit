from functools import wraps

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.request_validator import RequestValidator
from .settings import DJANGO_SMS_TOOLKIT_SETTINGS

from .models import TwilioMessage


def validate_twilio_request(f):
    """
    Validates that incoming requests genuinely originated from Twilio
    Docs: https://www.twilio.com/docs/usage/tutorials/how-to-secure-your-django-project-by-validating-incoming-twilio-requests
    """
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"]["AUTH_TOKEN"])

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.build_absolute_uri(),
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
        )

        # Continue processing the request if it's valid, return a 403 error if
        # it's not
        if request_valid or settings.DEBUG:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return decorated_function


@require_POST
@csrf_exempt
@validate_twilio_request
def twilio_status_callback_view(request, message_pk):
    with transaction.atomic():
        message = TwilioMessage.objects.select_for_update().get(pk=message_pk)
        message.status = request.POST["SmsStatus"]
        message.save()

    return HttpResponse(status=200)
