import json

from django.urls import reverse
from model_bakery import baker
from notifications.models import Notification

from jobs.models import Job
from users.models import User, OrganizationGroup, ObjectPermission
from users.util import update_organization_groups
from util.test_util import ClientLoginTestCase


class GroupStructureTests(ClientLoginTestCase):
    """Tests related to the visual group structure on the "Groups" page."""

    def setUp(self):
        super(GroupStructureTests, self).setUp()

        baker.make("users.Organization", name="SAEF")
        self.all_group = baker.make("users.OrganizationGroup", name="All")

        self.admin_group = baker.make("users.OrganizationGroup", name="Admin", parent=self.all_group)
        self.it_group = baker.make("users.OrganizationGroup", name="I.T.", parent=self.all_group)
        self.finance_group = baker.make("users.OrganizationGroup", name="Finance", parent=self.all_group)

    def load_blocks(self, file_name):
        """The block structures in the json files are automatically generated when the group structure is altered."""
        with open(f"database/data/test/users/group_blocks/{file_name}") as json_file:
            return json.load(json_file)

    def test_remove_group(self):
        self.assertTrue(OrganizationGroup.objects.filter(name="Finance").exists())

        # This user should get a notification when the "Finance" group is removed.
        notified_user = baker.make("users.User")
        notified_user.organization_groups.add(self.finance_group)

        # Load blocks where the group "Finance" is removed.
        blocks = self.load_blocks("group_blocks_removed_finance.json")
        update_organization_groups(blocks, self.user)

        self.assertFalse(OrganizationGroup.objects.filter(name="Finance").exists())
        self.assertTrue(Notification.objects.filter(recipient=notified_user).exists())

    def test_add_group(self):
        self.finance_group.delete()

        # Load blocks where the group "Finance" is added.
        blocks = self.load_blocks("group_blocks_added_finance.json")
        update_organization_groups(blocks, self.user)

        self.assertTrue(OrganizationGroup.objects.filter(name="Finance").exists())

    def test_move_group(self):
        self.assertTrue(self.finance_group.parent == OrganizationGroup.objects.get(name="All"))

        # Load blocks where the group "Finance" is moved to under the "Admin" group.
        blocks = self.load_blocks("group_blocks_moved_finance.json")
        update_organization_groups(blocks, self.user)

        self.finance_group.refresh_from_db()
        self.assertTrue(self.finance_group.parent == OrganizationGroup.objects.get(name="Admin"))


class GroupTablesTests(ClientLoginTestCase):
    """Tests related to the member and permission tables below the visual group structure on the "Groups" page."""

    def setUp(self):
        super(GroupTablesTests, self).setUp()

        baker.make("users.Organization", name="SAEF")
        self.all_group = baker.make("users.OrganizationGroup", name="All")

        self.admin_group = baker.make("users.OrganizationGroup", name="Admin", parent=self.all_group)
        self.it_group = baker.make("users.OrganizationGroup", name="I.T.", parent=self.all_group)
        self.finance_group = baker.make("users.OrganizationGroup", name="Finance", parent=self.all_group)

        self.user_2 = baker.make("users.User", is_active=True)
        self.job = Job.objects.create(name="test job", owner=self.user_2)

        self.user.organization_groups.add(self.all_group)
        self.user_2.organization_groups.add(self.all_group)

        self.user.is_staff = True
        self.user.save()

    def test_update_user_groups(self):
        form_data = {"organization_groups": [self.admin_group.id], "permission-select": []}
        self.client.post(reverse("update_groups_permissions", args=[self.user.id]), form_data)

        self.assertListEqual([self.all_group, self.admin_group], list(self.user.organization_groups.all()))
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())

    def test_update_user_permissions(self):
        level_2_perm = ObjectPermission.objects.get(object_id=self.job.id, can_update=True)
        form_data = {"organization_groups": [], "permission-select": [level_2_perm.id]}
        self.client.post(reverse("update_groups_permissions", args=[self.user.id]), form_data)

        self.assertListEqual([level_2_perm], list(self.user.object_permissions.all()))
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())

    def test_update_tables(self):
        """When a group in the visual structure is clicked, the member and permission tables should be updated."""
        self.user.organization_groups.add(self.admin_group)

        # Initially the "All" group is shown which contains both users but no permissions.
        all_response = self.client.get(reverse("update_tables"), {"group_name": "All"})

        # Note that assertCountEqual asserts that two iterables have the same elements, not just the same length.
        self.assertCountEqual([self.user, self.user_2], list(all_response.context["members"]))
        self.assertListEqual([], all_response.context["permissions"])

        # When the "Admin" group is clicked the tables should show the permissions and the single user in the group.
        admin_response = self.client.get(reverse("update_tables"), {"group_name": "Admin"})
        self.assertListEqual([self.user], admin_response.context["members"])
        self.assertListEqual(list(ObjectPermission.objects.all()), admin_response.context["permissions"])

    def test_update_tables_admin(self):
        """When an admin clicks the "Active" or "Inactive" blocks, show the active or inactive users in the table."""
        active_response = self.client.get(reverse("update_tables"), {"group_name": "Active"})
        self.assertListEqual([self.user_2], list(active_response.context["members"]))

        inactive_response = self.client.get(reverse("update_tables"), {"group_name": "Inactive"})
        self.assertListEqual([self.user], list(inactive_response.context["members"]))

    def test_toggle_active_user(self):
        self.assertIn(self.user_2, User.objects.filter(is_active=True))

        self.client.post(reverse("toggle_active"), {"group_name": "Active", "user_id": self.user_2.id})

        self.assertIn(self.user_2, User.objects.filter(is_active=False))

    def test_toggle_inactive_user(self):
        self.assertIn(self.user, User.objects.filter(is_active=False))

        self.client.post(reverse("toggle_active"), {"group_name": "Active", "user_id": self.user.id})

        self.assertIn(self.user, User.objects.filter(is_active=True))

    def test_group_add_member(self):
        self.user.organization_groups.add(self.admin_group)

        self.assertNotIn(self.admin_group, self.user_2.organization_groups.all())
        self.client.post(reverse("edit_group_objects"), {"group_name": "Admin", "object_type": "user",
                                                         "selected_objects": f"{self.user.id},{self.user_2.id}"})

        self.assertIn(self.admin_group, self.user_2.organization_groups.all())

        # One notification is sent to the added user and one to the other members of the group.
        self.assertTrue(Notification.objects.filter(recipient=self.user_2).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())

    def test_group_remove_member(self):
        self.user.organization_groups.add(self.admin_group)
        self.user_2.organization_groups.add(self.admin_group)

        self.assertIn(self.admin_group, self.user_2.organization_groups.all())
        self.client.post(reverse("edit_group_objects"), {"group_name": "Admin", "object_type": "user",
                                                         "selected_objects": f"{self.user.id}"})

        self.assertNotIn(self.admin_group, self.user_2.organization_groups.all())

        # One notification is sent to the removed user and one to the other members of the group.
        self.assertTrue(Notification.objects.filter(recipient=self.user_2).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())

    def test_group_add_permission(self):
        level_2_perm = ObjectPermission.objects.get(object_id=self.job.id, can_update=True)
        self.user.object_permissions.add(level_2_perm)

        self.assertNotIn(level_2_perm, self.all_group.object_permissions.all())
        self.client.post(reverse("edit_group_objects"), {"group_name": "All", "object_type": "permission",
                                                         "selected_objects": f"{level_2_perm.id}"})

        self.assertIn(level_2_perm, self.all_group.object_permissions.all())

        # One notification is sent to each member of the group which have had its permissions changed.
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.user_2).exists())

    def test_group_remove_permission(self):
        level_2_perm = ObjectPermission.objects.get(object_id=self.job.id, can_update=True)
        self.all_group.object_permissions.add(level_2_perm)

        self.assertIn(level_2_perm, self.all_group.object_permissions.all())
        self.client.post(reverse("edit_group_objects"), {"group_name": "All", "object_type": "permission",
                                                         "selected_objects": ""})

        self.assertNotIn(level_2_perm, self.all_group.object_permissions.all())

        # One notification is sent to each member of the group which have had its permissions changed.
        self.assertTrue(Notification.objects.filter(recipient=self.user).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.user_2).exists())
