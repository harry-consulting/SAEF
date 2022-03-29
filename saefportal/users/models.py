from collections import defaultdict
from itertools import chain

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from settings.models import Settings

# Using only the permissions name as the string representation instead of "application | model | permission name".
Permission.__str__ = lambda self: self.name
ContentType.__str__ = lambda self: self.name


class ObjectPermission(models.Model):
    can_view = models.BooleanField()
    can_update = models.BooleanField()
    can_delete = models.BooleanField()
    can_execute = models.BooleanField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.get_permission_string()} {self.get_object()}"

    def get_permission_string(self):
        permissions = [perm.title() for perm in ["view", "update", "delete", "execute"] if getattr(self, f"can_{perm}")]

        return f"Can {'/'.join(permissions)}"

    def get_object(self):
        return self.content_type.get_object_for_this_type(id=self.object_id)

    def get_permitted_groups(self):
        return [group.name for group in self.organizationgroup_set.all().order_by("name")]


class Organization(SingletonModel):
    name = models.CharField(max_length=50)
    group_structure = models.TextField(blank=True, null=True)
    settings = models.ForeignKey(Settings, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class OrganizationGroup(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)
    object_permissions = models.ManyToManyField(ObjectPermission, blank=True)

    def __str__(self):
        return self.name

    def get_ancestors(self):
        """Return the parents of the parents all the way up."""
        ancestors = []

        parent_group = self.parent
        while parent_group:
            ancestors.append(parent_group)
            parent_group = parent_group.parent

        return ancestors

    def get_all_children(self):
        """Return children's children all the way down."""
        all_child_groups = child_groups = list(OrganizationGroup.objects.filter(parent=self))

        while child_groups:
            child_groups = list(chain.from_iterable([list(OrganizationGroup.objects.filter(parent=group))
                                                     for group in child_groups]))
            all_child_groups.extend(child_groups)

        return all_child_groups

    def get_members(self):
        """Get all members of the group, including members of this groups child groups."""
        members = list(User.objects.filter(organization_groups__name=self.name))

        child_groups = self.get_all_children()
        [members.extend(list(User.objects.filter(organization_groups__name=group.name))) for group in child_groups]

        return list(set(members))

    def get_permissions(self):
        """Get all permissions of the group, including permissions of all groups hierarchically above this group."""
        permissions = list(self.object_permissions.all())

        for parent_group in self.get_ancestors():
            permissions += list(parent_group.object_permissions.all())

        return list(set(permissions))


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, is_active, **extra_fields):
        now = timezone.now()

        email = self.normalize_email(email)
        user = self.model(email=email, is_active=is_active, is_staff=is_staff, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self._create_user(email, password, False, False, False, **extra_fields)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, True, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name=_("email address"))
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    organization_groups = models.ManyToManyField(OrganizationGroup, blank=True, related_name="organization_groups")
    object_permissions = models.ManyToManyField(ObjectPermission, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_group_names(self):
        groups = []

        for group in self.organization_groups.all():
            groups.append(group.name)
            groups.extend([group.name for group in group.get_ancestors()])

        return list(set(groups))

    def get_group_object_permissions(self):
        group_permissions = []
        [group_permissions.extend(group.get_permissions()) for group in self.organization_groups.all()]

        return list(set(group_permissions))

    def get_all_object_permissions(self):
        return list(set(self.get_group_object_permissions() + list(self.object_permissions.all())))

    def has_permission(self, perm, obj):
        """Accepts permissions in the format 'action_model' such as perm='delete_connection'."""
        ct = ContentType.objects.get_for_model(obj)

        try:
            perm = perm.split('_')[0]
        except IndexError:
            return False

        all_permissions = self.get_all_object_permissions()
        return any([x for x in all_permissions
                    if x.content_type == ct and x.object_id == obj.id and getattr(x, f"can_{perm}")])

    def get_grouped_permissions(self):
        """Return the users object permissions grouped by the model name."""
        # Imported locally to avoid issues with circular imports.
        from users.util import group_permissions

        return group_permissions(self.get_all_object_permissions())

    def get_grouped_permission_ids(self):
        """
        Return dict that groups the permission ids by model name and permission level.
        This can be used to check for specific permissions in a template.
        """
        grouped_ids = {}

        for group, permissions in self.get_grouped_permissions().items():
            model_name = group.replace("(level 1)", "").replace("(level 2)", "").strip()

            if model_name not in grouped_ids:
                grouped_ids[model_name] = defaultdict(list)

            for permission in permissions:
                permission_level = "level_2" if "level 2" in group else "level_1"
                grouped_ids[model_name][permission_level].append(permission.object_id)

        return grouped_ids


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=32, default="")
    last_name = models.CharField(max_length=32, default="")
    phone = models.CharField(max_length=20, default="")
    settings = models.ForeignKey(Settings, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PermissionRequest(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "ACCEPTED", _("Accepted")
        DECLINED = "DECLINED", _("Declined")
        PENDING = "PENDING", _("Pending")

    requesting_user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now=True)

    # If null, the access is for the requesting user.
    group = models.ForeignKey(OrganizationGroup, on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(ObjectPermission, on_delete=models.CASCADE, blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    status_changed_at = models.DateTimeField(blank=True, null=True)

    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.permission.get_permission_string()} access to {self.permission.get_object()}"

    def get_status_icon(self):
        if self.status == self.Status.ACCEPTED:
            return '<i class="fas fa-check-circle success-green"></i>'
        elif self.status == self.Status.DECLINED:
            return '<i class="fas fa-exclamation-circle warning-red"></i>'
        elif self.status == self.Status.PENDING:
            return '<i class="fas fa-sync-alt"></i>'


class AdministrativeEvent(models.Model):
    event = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
