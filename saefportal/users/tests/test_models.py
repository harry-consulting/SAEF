from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from model_bakery import baker

from users.models import User, ObjectPermission
from util.test_util import ClientLoginTestCase, ClientLoginDatalakeTestCase


class UserManagerTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="test@test.com", password="test")

        self.assertEqual(user.email, "test@test.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(email="testsuper@test.com", password="test")

        self.assertEqual(admin_user.email, "testsuper@test.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


def create_basic_groups():
    baker.make("users.Organization", name="SAEF")
    all_group = baker.make("users.OrganizationGroup", name="All")

    admin_group = baker.make("users.OrganizationGroup", name="Admin", parent=all_group)
    it_group = baker.make("users.OrganizationGroup", name="I.T.", parent=all_group)
    team_a = baker.make("users.OrganizationGroup", name="Team A", parent=it_group)

    return all_group, admin_group, it_group, team_a


class ObjectPermissionTests(ClientLoginTestCase):
    def setUp(self):
        super(ObjectPermissionTests, self).setUp()

        self.all_group, self.admin_group, self.it_group, self.team_a = create_basic_groups()

        self.job = baker.make("jobs.Job", name="test", owner=self.user)
        self.level_2_perm = ObjectPermission.objects.filter(can_update=True).first()

    def test_get_permission_string(self):
        self.assertEqual("Can View/Update/Delete/Execute", self.level_2_perm.get_permission_string())

    def test_get_object(self):
        self.assertEqual(self.job, self.level_2_perm.get_object())

    def test_get_permitted_groups(self):
        self.all_group.object_permissions.add(self.level_2_perm)
        self.it_group.object_permissions.add(self.level_2_perm)

        # Note that the "Admin" groups gets the permissions by default.
        self.assertEqual(["Admin", "All", "I.T."], self.level_2_perm.get_permitted_groups())


class OrganizationGroupTests(ClientLoginTestCase):
    def setUp(self):
        super(OrganizationGroupTests, self).setUp()

        self.all_group, self.admin_group, self.it_group, self.team_a = create_basic_groups()

    def test_get_ancestors(self):
        self.assertCountEqual([self.it_group, self.all_group], self.team_a.get_ancestors())

    def test_get_all_children(self):
        self.assertCountEqual([self.admin_group, self.it_group, self.team_a], self.all_group.get_all_children())

    def test_get_members(self):
        """Members of a group should include the members of the child groups."""
        user_2 = baker.make("users.User")

        self.user.organization_groups.add(self.it_group)
        user_2.organization_groups.add(self.team_a)

        self.assertCountEqual([self.user, user_2], self.it_group.get_members())

    def test_get_permissions(self):
        """Permissions of a group should include the permissions of the groups hierarchically above the group."""
        baker.make("jobs.Job", name="test", owner=self.user)
        self.all_group.object_permissions.set(ObjectPermission.objects.all())

        self.assertCountEqual(list(ObjectPermission.objects.all()), self.it_group.get_permissions())


class UserTests(ClientLoginDatalakeTestCase):
    def setUp(self):
        super(UserTests, self).setUp()

        self.all_group, self.admin_group, self.it_group, self.team_a = create_basic_groups()

        self.user.organization_groups.add(self.all_group)
        self.user.organization_groups.add(self.it_group)

    def set_permissions(self, user, group):
        job_1 = baker.make("jobs.Job", name="test 1", owner=user)
        job_2 = baker.make("jobs.Job", name="test 2", owner=user)

        group.object_permissions.set(ObjectPermission.objects.filter(object_id=job_1.id))
        user.object_permissions.set(ObjectPermission.objects.filter(object_id=job_2.id))

        return job_1, job_2

    def create_objects(self, user):
        """Create a connection, dataset and job object and return the created level 2 permissions that the owner has."""
        connection = baker.make("datasets.Connection", name="test", owner=user, type="POSTGRES")
        dataset = baker.make("datasets.Dataset", name="test", owner=user, type="TABLE")
        job = baker.make("jobs.Job", name="test", owner=user)

        connection_perm = ObjectPermission.objects.get(content_type=ContentType.objects.get(model="connection"),
                                                       object_id=connection.id, can_update=True)
        dataset_perm = ObjectPermission.objects.get(content_type=ContentType.objects.get(model="dataset"),
                                                    object_id=dataset.id, can_update=True)
        job_perm = ObjectPermission.objects.get(content_type=ContentType.objects.get(model="job"),
                                                object_id=job.id, can_update=True)

        return connection_perm, dataset_perm, job_perm

    def test_get_group_names(self):
        self.assertCountEqual(["All", "I.T."], sorted(self.user.get_group_names()))

    def test_get_group_object_permissions(self):
        """Should only include the permissions of the users groups and not the users own permissions."""
        job_1, job_2 = self.set_permissions(self.user, self.it_group)

        self.assertCountEqual(list(ObjectPermission.objects.filter(object_id=job_1.id)),
                              self.user.get_group_object_permissions())

    def test_get_all_object_permissions(self):
        self.set_permissions(self.user, self.it_group)

        self.assertCountEqual(list(ObjectPermission.objects.all()), self.user.get_all_object_permissions())

    def test_has_permission(self):
        job_1, job_2 = self.set_permissions(self.user, self.it_group)
        job_3 = baker.make("jobs.Job", name="test")

        self.assertFalse(self.user.has_permission("update_job", job_3))
        self.assertTrue(self.user.has_permission("update_job", job_1))

    def test_get_grouped_permissions(self):
        connection_perm, dataset_perm, job_perm = self.create_objects(self.user)

        expected_grouped_permissions = {"connection (level 2)": [connection_perm], "dataset (level 2)": [dataset_perm],
                                        "job (level 2)": [job_perm]}
        self.assertEqual(expected_grouped_permissions, self.user.get_grouped_permissions())

    def test_get_grouped_permission_ids(self):
        connection_perm, dataset_perm, job_perm = self.create_objects(self.user)

        expected_grouped_permission_ids = {"connection": {"level_2": [connection_perm.object_id]},
                                           "dataset": {"level_2": [dataset_perm.object_id]},
                                           "job": {"level_2": [job_perm.object_id]}}

        self.assertEqual(expected_grouped_permission_ids, self.user.get_grouped_permission_ids())
