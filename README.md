# Django SMS Toolkit

Django module to send and store SMS with Twilio.

## Releases

To release a new version via github.com, follow the steps in this [link](https://help.github.com/en/articles/creating-releases).

To release a new version via git commands, follow this [documentation](https://git-scm.com/book/en/v2/Git-Basics-Tagging).

You can see the releases [here](https://github.com/Hipo/django-sms-toolkit/releases).

## Versioning

You can refer [here](https://semver.org/) for semantics of versioning.

## Installation

1. pip install `django-sms-toolkit`. 

2. Add **django_sms_toolkit** to the `INSTALLED_APPS` in the settings file.

3. Configure settings.

```
DJANGO_SMS_TOOLKIT_SETTINGS = {
    "SEND_SMS": True,  # True by default.
    "DEFAULT_FROM_NUMBER": "",
    "TWILIO": {
        "ACCOUNT_SID": "",
        "AUTH_TOKEN": "",
        "STATUS_CALLBACK_BASE_URL": "https://www.myapp.com",
        "TRIM_LONG_BODY": True,  # True by default. Makes sure character limit is not exceeded.
    }
}
```

4. `python manage.py migrate`

5. Include urls to be able to receive message status callbacks from Twilio.

```
urlpatterns = [
    ....,
    url(r'^', include('django_sms_toolkit.urls')),
]
```

6. (Optional) Add `TwilioMessageMixin` to your auth user model.
```
from django_sms_toolkit.models import TwilioMessageMixin

class AuthUser(TwilioMessageMixin,...):
    ....
    
# Default from number provided in settings is used if from_number is not provided.
user.send_sms(body, from_number=None)
# OR
from django_sms_toolkit.tasks import send_sms
send_sms.delay(from_number, to_number, body, recipient_id=None)
```

## Support

Please [open an issue](https://github.com/Hipo/django-sms-toolkit/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/Hipo/django-sms-toolkit/compare/).
