from itertools import chain

from django.urls import reverse_lazy
from notifications.signals import notify

from datasets.models import Connection, Dataset, DatasetRun
from jobs.models import Job
from users.models import OrganizationGroup, User, ObjectPermission, PermissionRequest, AdministrativeEvent


def get_saef_events():
    """Return list of SAEF object events specifying when objects were created, updated and deleted."""
    object_history = chain(Job.history.all(), Connection.history.all(), Dataset.history.all())

    return [{"type": object.history_object.__class__.__name__, "object": object.history_object,
             "action": object.get_history_type_display(), "by": object.history_user,
             "at": object.history_date} for object in object_history]


def get_run_events():
    return [{"task": run.task_name, "status": f"{run.get_status_icon()} {run.get_status_display()}",
             "by": run.created_by, "start": run.start_datetime, "end": run.end_datetime,
             "type": run.get_type_display()} for run in DatasetRun.objects.all()]


def update_organization_groups(blocks, user):
    """Update the OrganizationGroup objects based on given new group block structure."""
    current_groups = [group.name for group in OrganizationGroup.objects.all()]

    # Create or update groups.
    for block in blocks:
        group, created = OrganizationGroup.objects.get_or_create(name=block["attr"][2]["data-group-name"])
        parent_id = block["parent"]

        if parent_id != -1:
            parent_block = next(block for block in blocks if block["id"] == parent_id)
            group.parent = OrganizationGroup.objects.get(name=parent_block["attr"][2]["data-group-name"])

            group.save()

        if created:
            AdministrativeEvent.objects.create(event=f"Group '{group}' added to organization", created_by=user)
        else:
            current_groups.remove(group.name)

    # Delete groups that are no longer in the blocks.
    removed_groups = OrganizationGroup.objects.filter(name__in=current_groups)

    # Send a notification to the members of the removed groups.
    for group in removed_groups:
        notify.send(sender=user, recipient=User.objects.filter(organization_groups=group),
                    verb=f"removed {group.name} group", url=reverse_lazy("groups"))

        AdministrativeEvent.objects.create(event=f"Group '{group}' removed from organization", created_by=user)

    removed_groups.delete()


def update_group_members(group, selected_members, user):
    """Add/delete members from the given group based on the given list of selected members."""
    current_members = list(User.objects.filter(organization_groups__name=group.name))
    selected_members = [User.objects.get(id=object_id) for object_id in selected_members.split(",") if selected_members]

    # Add members to the group.
    for member in selected_members:
        if member not in current_members:
            member.organization_groups.add(group)
            member.save()

            # Send a notification to the added user, notifying them that they have been added to the group.
            notify.send(sender=user, recipient=member, verb="added you to group", action_object=group,
                        url=reverse_lazy("groups"))

            AdministrativeEvent.objects.create(event=f"User '{member}' added to group '{group}'", created_by=user)

    former_members = list(set(current_members) - set(selected_members))

    # Delete members from the group.
    for member in former_members:
        member.organization_groups.remove(group)
        member.save()

        # Send a notification to the removed user, notifying them that they have been removed from the group.
        notify.send(sender=user, recipient=member, verb="removed you from group", action_object=group,
                    url=reverse_lazy("groups"))

        AdministrativeEvent.objects.create(event=f"User '{member}' removed from group '{group}'", created_by=user)

    # Send a notification to the remaining members of the group, notifying them of the members being changed.
    remaining_members = list(set(current_members) - set(former_members))
    notify.send(sender=user, recipient=remaining_members, verb="changed the members of group", action_object=group,
                url=reverse_lazy("groups"))


def update_group_permissions(group, selected_permissions, user):
    """Add/delete permissions from the given group based on the given list of selected permissions."""
    user_permissions = user.get_all_object_permissions()
    current_permissions = list(group.object_permissions.all())

    selected_permissions = [ObjectPermission.objects.get(id=object_id) for object_id in selected_permissions.split(",")
                            if selected_permissions]

    # Add permissions to the group.
    for permission in selected_permissions:
        if permission not in current_permissions and permission in user_permissions:
            group.object_permissions.add(permission)
            AdministrativeEvent.objects.create(event=f"Permission '{permission}' given to group '{group}'",
                                               created_by=user)

    # Limit the current permissions to the permissions that the requesting user has. This is done to avoid removing
    # group permissions that were not selected due to the user not having permission to select/deselect it.
    current_permissions = [perm for perm in current_permissions if perm in user_permissions]
    former_permissions = list(set(current_permissions) - set(selected_permissions))

    # Delete permissions from the group.
    for permission in former_permissions:
        group.object_permissions.remove(permission)
        AdministrativeEvent.objects.create(event=f"Permission '{permission}' removed from group '{group}'",
                                           created_by=user)

    # Send a notification to the members of the group, notifying them of the permissions being changed.
    notify.send(sender=user, recipient=User.objects.filter(organization_groups=group),
                verb="changed the permissions of group", action_object=group, url=reverse_lazy("groups"))


def get_permission_sources(user, permissions):
    """Get a list of permission sources (groups or the user) for each permission."""
    permission_sources = []
    user_groups = set(user.get_group_names())

    for permission in permissions:
        permission_groups = {group.name for group in permission.organizationgroup_set.all()}
        group_sources = list(user_groups.intersection(permission_groups))

        user_source = ["User"] if user in permission.user_set.all() else []

        permission_sources.append(group_sources + user_source)

    return permission_sources


def give_permission(permission_request):
    """Give the permission from the permission request to the user or group."""
    permission = permission_request.permission
    obj = permission.get_object()

    if permission_request.group:
        group = permission_request.group
        group.object_permissions.add(permission)

        # Send a notification to the members of the group, notifying them of the permissions being changed.
        notify.send(sender=obj.owner, recipient=User.objects.filter(organization_groups=group),
                    verb="changed the permissions of group", action_object=group, url=reverse_lazy("groups"))

        AdministrativeEvent.objects.create(event=f"Permission '{permission}' given to group '{group}'",
                                           created_by=obj.owner)
    else:
        user = permission_request.requesting_user
        user.object_permissions.add(permission)
        AdministrativeEvent.objects.create(event=f"Permission '{permission}' given to user '{user}'",
                                           created_by=obj.owner)


def get_incoming_requests(user):
    """Return all requests for resources that the given user is an owner of."""
    pending = PermissionRequest.Status.PENDING
    pending_requests = PermissionRequest.objects.filter(status=pending).order_by("-requested_at")

    return [request for request in pending_requests if user == request.permission.get_object().owner]


def group_permissions(permissions):
    """Return the given object permissions grouped by the model name and permission level."""
    grouped_permissions = {"connection (level 1)": [], "connection (level 2)": [],
                           "dataset (level 1)": [], "dataset (level 2)": [],
                           "job (level 1)": [], "job (level 2)": []}

    for permission in permissions:
        group = f"{permission.get_object()._meta.model_name} (level {2 if permission.can_update else 1})"
        grouped_permissions[group].append(permission)

    # Order the permissions for each model.
    for _group_name, group_permissions in grouped_permissions.items():
        group_permissions.sort(key=lambda x: str(x))

    # Remove potentially empty permission lists.
    return {k: v for k, v in grouped_permissions.items() if v}
