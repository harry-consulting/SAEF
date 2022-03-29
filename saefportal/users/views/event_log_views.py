from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework_tracking.models import APIRequestLog

from users.models import AdministrativeEvent
from users.util import get_saef_events, get_run_events


@method_decorator(login_required, name="dispatch")
class EventLogView(TemplateView):
    template_name = "users/event_log.html"

    def get_context_data(self, **kwargs):
        context = super(EventLogView, self).get_context_data(**kwargs)
        context["api_events"] = APIRequestLog.objects.all()
        context["admin_events"] = AdministrativeEvent.objects.all()
        context["saef_events"] = get_saef_events()
        context["run_events"] = get_run_events()

        return context
