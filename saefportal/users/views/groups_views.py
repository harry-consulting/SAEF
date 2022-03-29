import json

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from notifications.signals import notify

from users.forms import UserGroupsPermissionsModelForm
from users.mixins import AdminPermissionRequiredMixin
from users.models import Organization, OrganizationGroup, User, AdministrativeEvent, ObjectPermission
from users.util import (update_group_members, update_group_permissions, update_organization_groups,
                        group_permissions)


@method_decorator(login_required, name="dispatch")
class GroupsView(TemplateView):
    template_name = "users/groups/groups.html"

    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data()
        context["group_structure"] = Organization.objects.get().group_structure

        return context


@method_decorator(login_required, name="dispatch")
class UserGroupsPermissionsUpdateView(AdminPermissionRequiredMixin, BSModalUpdateView):
    model = User
    template_name = "users/groups/update_user_groups_permissions.html"
    form_class = UserGroupsPermissionsModelForm
    success_url = reverse_lazy("groups")

    def get_context_data(self, **kwargs):
        context = super(UserGroupsPermissionsUpdateView, self).get_context_data(**kwargs)

        context["grouped_permissions"] = group_permissions(ObjectPermission.objects.all())
        context["initial_permissions"] = [perm.id for perm in self.object.object_permissions.all()]

        return context

    def form_valid(self, form):
        previous_groups = [str(group.id) for group in self.object.organization_groups.all()]
        previous_permissions = [str(perm.id) for perm in self.object.object_permissions.all()]
        self.object = form.save()

        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            self.object.object_permissions.set(self.request.POST.getlist("permission-select"))
            self.object.save()

            # If the groups or permissions were changed, notify the user of the change.
            all_group_id = OrganizationGroup.objects.get(name="All").id
            if set(previous_groups) != set(self.request.POST.getlist("organization_groups") + [str(all_group_id)]):
                notify.send(sender=self.request.user, recipient=self.get_context_data()["user"],
                            verb="changed your groups", url=reverse_lazy("groups"))

            if set(previous_permissions) != set(self.request.POST.getlist("permission-select")):
                notify.send(sender=self.request.user, recipient=self.get_context_data()["user"],
                            verb="changed your permissions", url=reverse_lazy("resource_access"))

        # Ensure the user is still a member of the "All" group.
        self.object.organization_groups.add(OrganizationGroup.objects.get(name="All"))

        return HttpResponseRedirect(self.get_success_url())


@login_required
def update_group_structure(request):
    """Called when the visual group structure in the UI is changed."""
    # Only update the structure if the requesting user is staff or an admin.
    if request.user.is_staff or OrganizationGroup.objects.get(name="Admin") in request.user.organization_groups.all():
        new_structure = request.POST.get("group_structure", None)

        blocks = json.loads(new_structure)["blocks"]
        block_names = [block["attr"][2]["data-group-name"] for block in blocks]

        # Only update the structure if the required "All" and "Admin" groups are present.
        if "All" in block_names and "Admin" in block_names:
            organization = Organization.objects.get()
            organization.group_structure = new_structure
            organization.save()

            update_organization_groups(blocks, request.user)

    return HttpResponse()


@login_required
def update_tables(request, group_name=None):
    """Return render of tables with user and permission data corresponding to the given group name."""
    user = request.user
    if group_name is None:
        group_name = request.GET.get("group_name", None)

    context = {"members": [], "permissions": [], "group_name": group_name, "admin": False, "users": User.objects.all(),
               "highlight_groups": []}

    if group_name == "Active" or group_name == "Inactive":
        # Only show the "Active" or "Inactive" group if the requesting user is staff or an admin.
        if user.is_staff or OrganizationGroup.objects.get(name="Admin") in user.organization_groups.all():
            context["members"] = User.objects.filter(is_active=group_name == "Active")
            context["admin"] = True
        else:
            context["group_name"] = "All"
            group_name = "All"

    if group_name != "Active" and group_name != "Inactive":
        group = OrganizationGroup.objects.get(name=group_name)
        context["members"] = group.get_members()

        context["permissions"] = group.get_permissions()
        context["highlight_groups"] = [group.name for group in group.get_all_children()] + [group_name]

    return render(request, "users/groups/tables.html", context)


@login_required
def toggle_active(request):
    """Toggle the "is_active" state of the given user."""
    group_name = request.POST.get("group_name", None)
    user_id = request.POST.get("user_id", None)
    user = User.objects.get(id=user_id)

    # Only toggle the active state if the requesting user is staff or an admin.
    if request.user.is_staff or OrganizationGroup.objects.get(name="Admin") in request.user.organization_groups.all():
        user.is_active = not user.is_active
        user.save()

        new_state = "Active" if user.is_active else "Inactive"
        AdministrativeEvent.objects.create(event=f"State changed to {new_state} for user '{user}'",
                                           created_by=request.user)
        new_members = User.objects.filter(is_active=not user.is_active)
    else:
        new_members = User.objects.filter(is_active=user.is_active)

    context = {"members": new_members, "group_name": group_name, "admin": True}
    return render(request, "users/groups/tables.html", context)


@login_required
def edit_group_objects(request):
    """Edit (add/remove) the members or permissions of the given group."""
    user = request.user
    group_name = request.POST.get("group_name", None)
    selected_objects = request.POST.get("selected_objects", None)
    object_type = request.POST.get("object_type", None)

    group = OrganizationGroup.objects.get(name=group_name)

    if object_type == "user":
        # Only update the group members if the requesting user is staff or an admin.
        if user.is_staff or OrganizationGroup.objects.get(name="Admin") in user.organization_groups.all():
            update_group_members(group, selected_objects, user)
    else:
        update_group_permissions(group, selected_objects, user)

    return update_tables(request, group_name=group_name)
