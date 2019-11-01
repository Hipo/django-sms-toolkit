from .settings import DJANGO_SMS_TOOLKIT_SETTINGS
from .tasks import send_sms as send_sms_task


def send_sms(to_number, body, recipient_id=None, from_number=None):
    if from_number is None:
        from_number = DJANGO_SMS_TOOLKIT_SETTINGS["DEFAULT_FROM_NUMBER"]

    return send_sms_task(from_number, to_number, body, recipient_id=None)
