from bootstrap_modal_forms.generic import BSModalReadView, BSModalCreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from notifications.signals import notify

from users.forms import PermissionRequestModelForm
from users.models import PermissionRequest, ObjectPermission
from users.util import give_permission, get_permission_sources, get_incoming_requests, group_permissions


def get_context_data(request):
    request_filter = PermissionRequest.objects.filter
    user_permissions = request.user.get_all_object_permissions()

    return {"user_permissions": zip(user_permissions, get_permission_sources(request.user, user_permissions)),
            "incoming_requests": get_incoming_requests(request.user),
            "outgoing_requests": request_filter(requesting_user=request.user).order_by("-status_changed_at")}


@method_decorator(login_required, name="dispatch")
class ResourceAccessView(TemplateView):
    template_name = "users/resource_access/resource_access.html"

    def get_context_data(self, **kwargs):
        return get_context_data(self.request)


@method_decorator(login_required, name="dispatch")
class PermissionRequestReadView(BSModalReadView):
    model = PermissionRequest
    template_name = "users/resource_access/read_permission_request.html"


@method_decorator(login_required, name="dispatch")
class PermissionRequestCreateView(BSModalCreateView):
    template_name = "users/resource_access/create_permission_request.html"
    form_class = PermissionRequestModelForm

    def get_context_data(self, **kwargs):
        context = super(PermissionRequestCreateView, self).get_context_data()
        context["grouped_permissions"] = group_permissions(ObjectPermission.objects.all())

        # If the request is from a user being denied access to a resource, add the required permission to the context.
        if self.kwargs:
            content_type = ContentType.objects.get(model=self.kwargs["resource_type"])
            permission = ObjectPermission.objects.get(content_type=content_type, object_id=self.kwargs["resource_id"],
                                                      can_update=self.kwargs["permission_level"] == 2)
            context["selected_permission"] = permission.id

        return context

    def get_form_kwargs(self):
        kwargs = super(PermissionRequestCreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            message = form.cleaned_data["message"]
            group = None if "access-for-group-checkbox" not in self.request.POST else form.cleaned_data["group"]

            # For each requested permission, create a permission request object.
            for permission_id in self.request.POST.getlist("permission-select"):
                permission = ObjectPermission.objects.get(id=permission_id)
                PermissionRequest.objects.create(requesting_user=self.request.user, group=group, permission=permission,
                                                 message=message)

                # Send a notification to the owner of the object with the request.
                notify.send(sender=self.request.user, recipient=permission.get_object().owner,
                            verb="requested permission", action_object=permission, url=reverse_lazy("resource_access"))

            messages.success(self.request, "Permission request was sent.")

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("resource_access")


@login_required
def reply_to_request(request):
    """Handle the given reply to the given resource request."""
    reply = request.POST.get("reply", None) == "true"
    permission_request_id = request.POST.get("permission_request_id", None)

    permission_request = PermissionRequest.objects.get(id=permission_request_id)

    # Only reply to the request if the reply is from the owner of the requested resource.
    if permission_request.permission.get_object().owner == request.user:
        permission_request.status = PermissionRequest.Status.ACCEPTED if reply else PermissionRequest.Status.DECLINED
        permission_request.status_changed_at = timezone.now()
        permission_request.save()

        if reply:
            give_permission(permission_request)

        # Send a notification to the requesting user with the reply.
        verb = "accepted" if reply else "declined"
        notify.send(sender=permission_request.permission.get_object().owner, recipient=permission_request.requesting_user,
                    verb=f"{verb} request for permission", action_object=permission_request.permission,
                    url=reverse_lazy("resource_access"))

    return render(request, "users/resource_access/incoming_outgoing_requests.html", get_context_data(request))
