from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from datasets.models import Connection, Dataset
from jobs.models import Job
from users.models import ObjectPermission, OrganizationGroup


@receiver(post_save, sender=Connection)
@receiver(post_save, sender=Dataset)
@receiver(post_save, sender=Job)
def create_object_permissions(instance, created, **kwargs):
    """
    Create both a level 1 and level 2 object permission when a connection, dataset or job is created. Both permissions
    are given to the admin group by default and the level 2 permission is given to the owner of the new object.
    """
    if created:
        content_type = ContentType.objects.get_for_model(instance)

        permissions = {"can_view": True, "can_update": False, "can_delete": False, "can_execute": False}

        # Create the level 1 object permission.
        level_1 = ObjectPermission.objects.create(**permissions, content_type=content_type, object_id=instance.id)

        permissions["can_update"] = True
        permissions["can_delete"] = True

        if content_type.name == "job":
            permissions["can_execute"] = True

        # Create the level 2 object permission.
        level_2 = ObjectPermission.objects.create(**permissions, content_type=content_type, object_id=instance.id)

        # Give the new permissions to the admin group and the owner of the object, if possible.
        admin_group = OrganizationGroup.objects.filter(name="Admin").first()
        if admin_group:
            admin_group.object_permissions.add(level_1)
            admin_group.object_permissions.add(level_2)

        if instance.owner:
            instance.owner.object_permissions.add(level_2)


@receiver(pre_save, sender=Connection)
@receiver(pre_save, sender=Dataset)
@receiver(pre_save, sender=Job)
def transfer_owner_permission(instance, **kwargs):
    """
    When the owner of a connection, dataset or job is changed, give the new owner level 2 permission and remove
    the permission from the previous owner.
    """
    if instance.id is not None:
        content_type = ContentType.objects.get_for_model(instance)
        previous = type(instance).objects.get(id=instance.id)

        if previous.owner and previous.owner != instance.owner:
            level_2 = ObjectPermission.objects.get(can_update=True, content_type=content_type, object_id=instance.id)

            instance.owner.object_permissions.add(level_2)
            previous.owner.object_permissions.remove(level_2)


@receiver(post_delete, sender=Connection)
@receiver(post_delete, sender=Dataset)
@receiver(post_delete, sender=Job)
def delete_object_permissions(instance, **kwargs):
    """Delete the related object permissions when a connection, dataset or job is deleted."""
    content_type = ContentType.objects.get_for_model(instance)
    ObjectPermission.objects.filter(content_type=content_type, object_id=instance.id).delete()
