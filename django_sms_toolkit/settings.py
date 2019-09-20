from django.conf import settings

DJANGO_SMS_TOOLKIT_SETTINGS = getattr(settings, "DJANGO_SMS_TOOLKIT_SETTINGS", {})

DJANGO_SMS_TOOLKIT_SETTINGS.setdefault("SEND_SMS", True)
DJANGO_SMS_TOOLKIT_SETTINGS.setdefault("DEFAULT_FROM_NUMBER", "")
DJANGO_SMS_TOOLKIT_SETTINGS.setdefault("TWILIO", {})
DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"].setdefault("ACCOUNT_SID", "")
DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"].setdefault("AUTH_TOKEN", "")
DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"].setdefault("STATUS_CALLBACK_BASE_URL", "")
DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"].setdefault("TRIM_LONG_BODY", True)


if DJANGO_SMS_TOOLKIT_SETTINGS["SEND_SMS"]:
    required_twilio_fields = ["ACCOUNT_SID", "AUTH_TOKEN", "STATUS_CALLBACK_BASE_URL"]
    for field_name in required_twilio_fields:
        if not DJANGO_SMS_TOOLKIT_SETTINGS["TWILIO"].get(field_name):
            assert False, "DJANGO_SMS_TOOLKIT_SETTINGS['TWILIO']: {} is required.".format(field_name)
