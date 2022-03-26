from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from home.util import get_job_usage_data, get_api_usage_data


@method_decorator(login_required, name="dispatch")
class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context["job_usage_data"] = get_job_usage_data()
        context["api_usage_data"] = get_api_usage_data()

        return context
