from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from users.models import OrganizationGroup, User, AdministrativeEvent


class ObjectPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Mixin used in views that need to limit user access based on the users object permissions. For views that don't
    trigger a modal normally (for example delete views), we also handle the object permissions in the UI.
    """

    def has_permission(self):
        return self.request.user.has_permission(self.object_permission, self.model.objects.get(id=self.kwargs["pk"]))

    def handle_no_permission(self):
        """Redirecting to the permission request modal if permission was denied."""
        permission_level = 1 if "view" in self.object_permission else 2

        return HttpResponseRedirect(reverse_lazy("request_access", kwargs={"resource_type": self.model.__name__.lower(),
                                                                           "resource_id": self.kwargs["pk"],
                                                                           "permission_level": permission_level}))


class AdminPermissionRequiredMixin(PermissionRequiredMixin):
    """Mixin used in views that need to limit user access based on if the requesting user has admin permissions."""

    def has_permission(self):
        user = self.request.user
        return user.is_staff or OrganizationGroup.objects.get(name="Admin") in user.organization_groups.all()


class LogOwnerUpdatesMixin:
    """Mixin used in model forms that need to create an administrative event when the owner is updated."""

    def save(self, commit=True):
        obj = super(LogOwnerUpdatesMixin, self).save(commit=False)

        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            # If the object was updated and the owner was changed, create an administrative event.
            if obj.pk and "owner" in self.changed_data:
                owner = User.objects.get(id=self.data["owner"])
                model_name = obj._meta.model.__name__.lower()

                AdministrativeEvent.objects.create(event=f"Ownership of {model_name} '{obj}' given to user '{owner}'",
                                                   created_by=self.request.user)

            if commit:
                obj.save()

        return obj
