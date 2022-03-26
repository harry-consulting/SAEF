from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from datasets.models import Connection
from users.models import ObjectPermission
from util.test_util import ClientLoginDatalakeTestCase


class CreateObjectPermissionsSignalTests(ClientLoginDatalakeTestCase):
    """
    When a connection, dataset or job is created, object permissions should be created for the object. Both level 1 and
    2 permissions should be given to the "Admin" group and level 2 permission should be given to the owner.
    """

    def assert_object_permissions_exist(self, obj):
        ct = ContentType.objects.get_for_model(obj)

        self.assertTrue(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=False).exists())
        self.assertTrue(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=True).exists())

    def test_connection_create_object_permission(self):
        connection = baker.make("datasets.Connection", name="test", owner=self.user, type=Connection.Type.POSTGRES)

        self.assert_object_permissions_exist(connection)

    def test_dataset_create_object_permission(self):
        dataset = baker.make("datasets.Dataset", name="test", owner=self.user)

        self.assert_object_permissions_exist(dataset)

    def test_job_create_object_permission(self):
        job = baker.make("jobs.Job", name="test", owner=self.user)

        self.assert_object_permissions_exist(job)

    def test_permissions_given_to_admin_group(self):
        admin_group = baker.make("users.OrganizationGroup", name="Admin")
        baker.make("datasets.Connection", name="test", owner=self.user, type=Connection.Type.POSTGRES)

        self.assertCountEqual(list(ObjectPermission.objects.all()), list(admin_group.object_permissions.all()))

    def test_level_2_permission_given_to_owner(self):
        baker.make("datasets.Connection", name="test", owner=self.user, type=Connection.Type.POSTGRES)
        level_2_perm = ObjectPermission.objects.filter(can_update=True).first()

        self.assertEqual([level_2_perm], list(self.user.object_permissions.all()))


class TransferOwnerPermissionSignalTests(ClientLoginDatalakeTestCase):
    """
    When the owner of a connection is changed, the new owner should get level 2 permission and the permission
    should be removed from the old owner.
    """

    def setUp(self):
        super(TransferOwnerPermissionSignalTests, self).setUp()

        self.user_2 = baker.make("users.User")

    def assert_object_permission_transfers(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        level_2_perm = ObjectPermission.objects.get(content_type=ct, object_id=obj.id, can_update=True)

        self.assertTrue(self.user.object_permissions.filter(id=level_2_perm.id).exists())

        obj.owner = self.user_2
        obj.save()

        self.assertFalse(self.user.object_permissions.filter(id=level_2_perm.id).exists())
        self.assertTrue(self.user_2.object_permissions.filter(id=level_2_perm.id).exists())

    def test_connection_transfer_owner_permissions(self):
        connection = baker.make("datasets.Connection", name="test", owner=self.user, type=Connection.Type.POSTGRES)

        self.assert_object_permission_transfers(connection)

    def test_dataset_transfer_owner_permissions(self):
        dataset = baker.make("datasets.Dataset", name="test", owner=self.user)

        self.assert_object_permission_transfers(dataset)

    def test_job_transfer_owner_permissions(self):
        job = baker.make("jobs.Job", name="test", owner=self.user)

        self.assert_object_permission_transfers(job)


class DeleteObjectPermissionsSignalTests(ClientLoginDatalakeTestCase):
    """When a connection, dataset or job is deleted, the related object permissions should be deleted."""

    def assert_object_permissions_deleted(self, obj):
        ct = ContentType.objects.get_for_model(obj)

        self.assertTrue(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=False).exists())
        self.assertTrue(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=True).exists())

        obj.delete()

        self.assertFalse(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=False).exists())
        self.assertFalse(ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, can_update=True).exists())

    def test_connection_delete_object_permission(self):
        connection = baker.make("datasets.Connection", name="test", owner=self.user, type=Connection.Type.POSTGRES)

        self.assert_object_permissions_deleted(connection)

    def test_dataset_delete_object_permission(self):
        dataset = baker.make("datasets.Dataset", name="test", owner=self.user)

        self.assert_object_permissions_deleted(dataset)

    def test_job_delete_object_permission(self):
        job = baker.make("jobs.Job", name="test", owner=self.user)

        self.assert_object_permissions_deleted(job)
