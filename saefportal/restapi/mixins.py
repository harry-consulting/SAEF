from rest_framework_tracking.mixins import LoggingMixin

from restapi.util import get_access_dependant_object


class BasicLoggingMixin(LoggingMixin):
    """Mixin that provides logging without saving the query parameters and the response, used for security reasons."""
    def handle_log(self):
        self.log["query_params"] = {}
        self.log["response"] = ""
        super(BasicLoggingMixin, self).handle_log()


class FilterQuerysetByObjectPermissionMixin:
    """Mixin used in views that need to filter the objects shown in the list endpoints by object permission."""

    def get_queryset(self):
        permitted_objects = []

        for obj in self.queryset:
            access_object = get_access_dependant_object(type(obj).__name__, obj)

            if self.request.user.has_permission(self.object_permission, access_object):
                permitted_objects.append(obj.id)

        return self.queryset.model.objects.filter(id__in=permitted_objects).order_by("id")
