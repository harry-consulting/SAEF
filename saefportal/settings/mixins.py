from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from settings.models import Settings


class DatalakeRequiredMixin(PermissionRequiredMixin):
    """Mixin used in views that need to limit user access based on whether a current datalake connection exists."""

    def has_permission(self):
        return Settings.objects.get().datalake is not None

    def handle_no_permission(self):
        """Redirecting to the datalake connection modal if permission was denied."""
        return HttpResponseRedirect(reverse_lazy("settings:create_datalake_connection", kwargs={"redirect": "true"}))
