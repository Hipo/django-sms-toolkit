import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .settings import DJANGO_SMS_TOOLKIT_SETTINGS


class TwilioMessage(models.Model):

    # Outgoing Statuses
    STATUS_ACCEPTED = "accepted"

    # This is a status that is not exist in the Twilio.
    # It will be used for the messages that is not accepted by the twilio.
    # For example in a case where phone number is not valid.
    STATUS_REJECTED = "rejected"

    STATUS_QUEUED = "queued"
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_UNDELIVERED = "undelivered"
    STATUS_FAILED = "failed"

    # Incoming Statuses
    STATUS_RECEIVED = "received"

    STATUSES = (
        (STATUS_REJECTED, STATUS_REJECTED),
        (STATUS_ACCEPTED, STATUS_ACCEPTED),
        (STATUS_QUEUED, STATUS_QUEUED),
        (STATUS_SENT, STATUS_SENT),
        (STATUS_DELIVERED, STATUS_DELIVERED),
        (STATUS_UNDELIVERED, STATUS_UNDELIVERED),
        (STATUS_FAILED, STATUS_FAILED),
        (STATUS_RECEIVED, STATUS_RECEIVED),
    )

    TYPE_INCOMING = "incoming"
    TYPE_OUTGOING = "outgoing"

    TYPES = (
        (TYPE_INCOMING, TYPE_INCOMING),
        (TYPE_OUTGOING, TYPE_OUTGOING),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="twilio_messages", on_delete=models.SET_NULL, null=True, blank=True)
    message_sid = models.CharField(max_length=512, null=True, blank=True, unique=True)
    type = models.CharField(choices=TYPES, max_length=32)
    status = models.CharField(choices=STATUSES, max_length=32, blank=True)
    from_number = models.CharField(max_length=255)
    to_number = models.CharField(max_length=255)

    # The message body aimed to be send. If the message trimming is active and
    # message is too long, `body` will store the trimmed version of the message.
    # For example:
    # original_body = ".....and say hello lorem sit...."
    # body = ".......and s"
    original_body = models.TextField()
    body = models.TextField()

    # TwilioRestException message if exists.
    exception_message = models.TextField(blank=True)

    creation_datetime = models.DateTimeField(default=timezone.now)
    update_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Twilio message from {from_number} to {to_number}".format(from_number=self.from_number, to_number=self.to_number)

    class Meta:
        verbose_name = _('Twilio Message')
        verbose_name_plural = _('Twilio Messages')
        ordering = ["-creation_datetime"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super(TwilioMessage, self).clean()

        if self.type == self.TYPE_INCOMING and self.status and self.status != self.STATUS_RECEIVED:
            raise ValidationError("Incoming message status is not valid.")

        if self.type == self.TYPE_OUTGOING and self.status == self.STATUS_RECEIVED:
            raise ValidationError("Outgoing message status is not valid.")

        if not self._state.adding and self.type == self.TYPE_OUTGOING:
            # https://support.twilio.com/hc/en-us/articles/223134347-What-are-the-Possible-SMS-and-MMS-Message-Statuses-and-What-do-They-Mean-
            ongoing_statuses = [self.STATUS_ACCEPTED, self.STATUS_QUEUED, self.STATUS_SENT]
            finalized_statuses = [self.STATUS_DELIVERED, self.STATUS_UNDELIVERED, self.STATUS_FAILED]

            # https://docs.djangoproject.com/en/2.2/ref/models/instances/#refreshing-objects-from-database
            new_status = self.status
            del self.status
            # Fetch status from database.
            old_status = self.status

            if old_status in finalized_statuses and new_status in ongoing_statuses:
                raise ValidationError(
                    "Cannot revert status of outgoing message ({id}) from {old_status} to {new_status}".format(
                        id=self.id,
                        old_status=old_status,
                        new_status=new_status,
                    )
                )
            else:
                self.status = new_status


class TwilioMessageMixin(object):

    def get_phone_number(self):
        return self.phone_number

    def send_sms(self, body, from_number=None):
        from .tasks import send_sms

        if not DJANGO_SMS_TOOLKIT_SETTINGS["SEND_SMS"]:
            return 'Cannot send SMS because of environment settings.'

        from_number = from_number or DJANGO_SMS_TOOLKIT_SETTINGS["DEFAULT_FROM_NUMBER"]
        assert from_number

        if isinstance(self, get_user_model()):
            recipient_id = self.pk
        else:
            recipient_id = None

        send_sms.delay(from_number, self.get_phone_number(), body, recipient_id=recipient_id)
