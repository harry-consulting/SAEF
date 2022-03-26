from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from solo.admin import SingletonModelAdmin

from .models import (User, UserProfile, OrganizationGroup, Organization, PermissionRequest, ObjectPermission,
                     AdministrativeEvent)


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "is_staff")
    list_filter = ("is_staff",)
    fieldsets = ((None, {"fields": ("email", "password", "organization_groups", "object_permissions")}),
                 ("Permissions", {"fields": ("is_staff", "is_active")}),)
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Organization, SingletonModelAdmin)
admin.site.register(OrganizationGroup)
admin.site.register(UserProfile)
admin.site.register(PermissionRequest)
admin.site.register(ObjectPermission)
admin.site.register(AdministrativeEvent)
