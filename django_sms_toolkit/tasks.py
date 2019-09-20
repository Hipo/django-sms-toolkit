from celery import shared_task
from django.urls import reverse
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from .models import TwilioMessage
from .settings import DJANGO_SMS_TOOLKIT_SETTINGS


@shared_task(retry_backoff=30, retry_kwargs={'max_retries': 3})
def send_sms(from_number, to_number, body, recipient_id=None):
    if not DJANGO_SMS_TOOLKIT_SETTINGS["SEND_SMS"]:
        return 'Cannot send SMS because of environment settings.'

    # Twilio does not accept body larger than 1600 characters. https://www.twilio.com/docs/api/errors/21617
    # If the body is larger than 1600, Send the first 1600 chars.
    original_body = body

    if DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"]["TRIM_LONG_BODY"]:
        body = body[0:1600]

    # Create twilio message before calling twilio.
    # If twilio message object created after message is sent to Twilio, race condition occurs.
    # Some times Twilio calls status callback before the transaction is completed and message is saved.
    twilio_message = TwilioMessage.objects.create(
        recipient_id=recipient_id,
        type=TwilioMessage.TYPE_OUTGOING,
        from_number=from_number,
        to_number=to_number,
        original_body=original_body,
        body=body
    )

    client = Client(DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"]["ACCOUNT_SID"], DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"]["AUTH_TOKEN"])

    try:
        message = client.messages.create(
            from_=from_number,
            to=to_number,
            body=body,
            status_callback=DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"]["STATUS_CALLBACK_BASE_URL"].strip("/") + reverse("twilio-status-callback", args=[twilio_message.id])
        )
        # NOTE: Status will be saved by status callback view.
        twilio_message.message_sid = message.sid
        twilio_message.save(update_fields=["message_sid"])
    except TwilioRestException as error:
        twilio_message.status = TwilioMessage.STATUS_REJECTED
        twilio_message.exception_message = error.__repr__()
        twilio_message.save()

        if error.code in (21211, 21614):  # Invalid Number
            return "Phone number is invalid. Failed saliently."
        else:
            raise error
