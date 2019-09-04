from django.contrib import admin

from .models import TwilioMessage


class TwilioMessageAdmin(admin.ModelAdmin):

    search_fields = ["message_sid", "original_body", "from_number", "to_number"]
    list_filter = ["status", "type"]
    list_display = ["id", "message_sid", "recipient", "from_number", "to_number", "body", "type", "status"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(TwilioMessage, TwilioMessageAdmin)
