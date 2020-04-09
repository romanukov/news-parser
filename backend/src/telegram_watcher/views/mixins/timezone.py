from django.utils import timezone
import pytz


class APIUserTimezone:
    def initial(self, request, *args, **kwargs):
        tzname = getattr(request.user, "timezone", 'UTC')
        timezone.activate(pytz.timezone(tzname))
        return super().initial(request, *args, **kwargs)
