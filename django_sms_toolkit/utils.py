from .tasks import send_sms as send_sms_task


def send_sms(from_number, to_number, body, recipient_id=None):
    return send_sms_task(from_number, to_number, body, recipient_id=None)
