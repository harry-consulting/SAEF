from saef.connections import ConnectionFormHelper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from django.urls import reverse
from django.test import TestCase, RequestFactory, tag
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from analyzer.utilities import decrypt
from ..models import Connection, PostgresConnection, ConnectionType as ConnectionTypeModel
from ..views import update_connection
from users.models import User
from saef.enums import ConnectionType as ConnectionType

def assert_all_postgres_fields_equal(saved_postgres_connection, postgres_form, saved_connection, connection_form):
    test = TestCase()

    test.assertEqual(saved_postgres_connection.username, postgres_form["username"])
    test.assertEqual(decrypt(saved_postgres_connection.password), postgres_form["password"])
    test.assertEqual(saved_postgres_connection.host, postgres_form["host"])
    test.assertEqual(saved_postgres_connection.port, int(postgres_form["port"]))
    test.assertEqual(saved_postgres_connection.db_name, postgres_form["db_name"])
    test.assertEqual(saved_postgres_connection.connection.id, saved_connection.id)

    test.assertEqual(saved_connection.name, postgres_form["connection_name"])
    test.assertEqual(saved_connection.time_out, postgres_form["time_out"])
    test.assertEqual(saved_connection.connection_type.id, connection_form["connection_type"].id)


def setup_valid_postgres_connection():
    return {
        "connection_name": "SQL",
        "db_name": "saefportal",
        "username": "saefuser",
        "password": "saefpassword",
        "host": "127.0.0.1",
        "port": 5432,
        "time_out": 120
    }

def setup_valid_connection():
    return {
        'connection_name': 'SQL',
        'time_out': 300,
        'connection_type': ConnectionTypeModel.objects.create(name="PostgreSQL", version="latest version"),
    }

def setup_middleware(request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    middleware = MessageMiddleware()
    middleware.process_request(request)
    request.session.save()


class TestManageConnection(TestCase):
    def assert_old_new(self, old, new, value):
        self.test.assertNotEqual(old, new)
        self.test.assertEqual(value, new)

    def update_connection(self, field_to_edit, value):
        data = self.edit_postgres_connection_form
        data["connection_type"] = 1
        data[field_to_edit] = value
        data["Operation"] = "update"

        request = self.factory.post(reverse("connection_detail", kwargs={"connection_id": self.saved_connection.id}),
                                    data)
        request.user = self.user
        setup_middleware(request)

        update_connection(request, self.saved_connection.id)

    def assert_edit(self, field_to_edit, value):
        self.update_connection(field_to_edit, value)
        return Connection.objects.get(id=self.saved_connection.id)

    def assert_postgres_edit(self, field_to_edit, value):
        self.update_connection(field_to_edit, value)
        return PostgresConnection.objects.get(id=self.saved_postgres_connection.id)

    @classmethod
    def setUp(cls):
        helper = ConnectionFormHelper()
        cls.connection_form_helper = helper.connection_form

        cls.connection_form = setup_valid_connection()

        cls.add_postgres_connection_form = {
            "connection_name": "test connection name",
            "db_name": "test database name",
            "username": "test username",
            "password": "test password",
            "host": "test host",
            "port": 1234,
            "time_out": 120
        }

        cls.edit_postgres_connection_form = {
            "connection_name": "test connection name",
            "db_name": "test database name",
            "username": "test username",
            "host": "test host",
            "port": 1234,
            "time_out": 120
        }

        cls.connection_form_helper[ConnectionType.POSTGRES.value]['save'](cls.add_postgres_connection_form, cls.connection_form)

        cls.saved_postgres_connection = PostgresConnection.objects.get(
            db_name=cls.add_postgres_connection_form["db_name"])

        cls.saved_connection = Connection.objects.get(name=cls.add_postgres_connection_form["connection_name"])
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user("email@company.com", "password")

        cls.test = TestCase()

    def test_should_add_postgres_connection(self):
        assert_all_postgres_fields_equal(self.saved_postgres_connection, self.add_postgres_connection_form,
                                         self.saved_connection, self.connection_form)

    def test_should_successfully_test_connection_if_valid(self):
        postgres_form = setup_valid_postgres_connection()
        connection = setup_valid_connection()
        self.assertTrue(self.connection_form_helper[ConnectionType.POSTGRES.value]['test'](postgres_form, connection))

    def test_should_unsuccessfully_test_connection_if_invalid(self):
        connection = setup_valid_connection()
        self.assertFalse(self.connection_form_helper[ConnectionType.POSTGRES.value]['test'](self.add_postgres_connection_form, 
                                                                                         connection))

    def test_should_edit_postgres_connection_db_name(self):
        value = "test edited database name"
        updated_postgres_connection = self.assert_postgres_edit("db_name", value)
        self.assert_old_new(self.saved_postgres_connection.db_name, updated_postgres_connection.db_name, value)

    def test_should_edit_postgres_connection_username(self):
        value = "test edited username"
        updated_postgres_connection = self.assert_postgres_edit("username", value)
        self.assert_old_new(self.saved_postgres_connection.username, updated_postgres_connection.username, value)

    def test_should_edit_postgres_connection_host(self):
        value = "test edit host"
        updated_postgres_connection = self.assert_postgres_edit("host", value)
        self.assert_old_new(self.saved_postgres_connection.host, updated_postgres_connection.host, value)

    def test_should_edit_postgres_connection_port(self):
        value = 9876
        updated_postgres_connection = self.assert_postgres_edit("port", value)
        self.assert_old_new(self.saved_postgres_connection.port, updated_postgres_connection.port, value)

    def test_should_delete_postgres_connection(self):
        data = {"Operation": "Delete"}
        request = self.factory.post(reverse("connection_detail", kwargs={"connection_id": self.saved_connection.id}),
                                    data)
        request.user = self.user
        setup_middleware(request)

        update_connection(request, self.saved_connection.id)
        self.test.assertRaises(Connection.DoesNotExist, Connection.objects.get, id=self.saved_connection.id)

    def test_should_edit_connection_name(self):
        value = "test edited connection name"
        updated_connection = self.assert_edit("connection_name", value)
        self.assert_old_new(self.saved_connection.name, updated_connection.name, value)

    def test_should_edit_connection_time_out(self):
        value = 240
        updated_connection = self.assert_edit("time_out", value)
        self.assert_old_new(self.saved_connection.time_out, updated_connection.time_out, value)


def logInWithBrowser(browser):
    browser.get("localhost:8000/user/login/")
    browser.find_element_by_id("id_email").send_keys("test@test.test")
    browser.find_element_by_id("id_password").send_keys("l")
    browser.find_element_by_class_name("btn-outline-info").send_keys(Keys.RETURN)


def submitConnectionType(browser):
    select = Select(browser.find_element_by_id("id_connection_type"))
    select.select_by_visible_text("PostgreSQL")
    select = Select(browser.find_element_by_id("id_connection_type"))
    connection_type = select.first_selected_option.text
    return connection_type


def fillConnectionForm(browser):
    browser.find_element_by_id("id_db_name").send_keys("6")
    browser.find_element_by_id("id_username").send_keys("6")
    browser.find_element_by_id("id_password").send_keys("6")
    browser.find_element_by_id("id_host").send_keys("6")
    browser.find_element_by_id("id_port").send_keys(6)
    browser.find_element_by_id("id_time_out").send_keys(6)
    return {
        "db_name": "6",
        "username": "6",
        "password": "6",
        "host": "6",
        "port": 6,
        "time_out": 6
    }


def pressTestButton(browser):
    browser.find_element_by_id("id_test_button").send_keys(Keys.RETURN)


def getSelectedConnectionType(browser):
    select = Select(browser.find_element_by_xpath("//select"))
    return select.first_selected_option.text


def getConnectionFormData(browser):
    return {
        "db_name": browser.find_element_by_id("id_db_name").get_attribute("value"),
        "username": browser.find_element_by_id("id_username").get_attribute("value"),
        "password": browser.find_element_by_id("id_password").get_attribute("value"),
        "host": browser.find_element_by_id("id_host").get_attribute("value"),
        "port": browser.find_element_by_id("id_port").get_attribute("value"),
        "time_out": browser.find_element_by_id("id_time_out").get_attribute("value")
    }


@tag('selenium')
class TestManageConnectionInBrowser(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.browser = webdriver.Chrome()
        cls.add_connection_url = "localhost:8000{0}".format(reverse("add_connection"))
        logInWithBrowser(cls.browser)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()

    def test_test_connection_should_not_clear_connection_type(self):
        self.browser.get(self.add_connection_url)
        old_connection_type = submitConnectionType(self.browser)
        fillConnectionForm(self.browser)
        pressTestButton(self.browser)
        new_connection_type = getSelectedConnectionType(self.browser)

        self.assertEqual(old_connection_type, new_connection_type)
