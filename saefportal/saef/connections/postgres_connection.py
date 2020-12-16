
from saef.models import PostgresConnection
from saef.forms import AddPostgresConnectionForm, EditPostgresConnectionForm
from analyzer.datastore import DatastorePostgres
from analyzer.utilities import encrypt

from .utils import create_connection, test_connection, save_connection, save_edit_connection_form, edit_connection


def postgres_form_helper():
    return {'add': AddPostgresConnectionForm,
            'edit': edit_postgres_connection,
            'save': save_postgres_connection,
            'save_edit': save_edit_postgres_connection,
            'test': test_postgres_connection}


def postgres_connection(postgres_form, form):
    connection = create_connection(postgres_form, form)

    db_name = postgres_form["db_name"]
    username = postgres_form["username"]
    password = encrypt(postgres_form["password"])
    host = postgres_form["host"]
    port = postgres_form["port"]

    postgres_connection = PostgresConnection(
        db_name=db_name,
        username=username,
        password=password,
        host=host,
        port=port,
        connection=connection
    )

    return connection, postgres_connection


def save_edit_postgres_connection_form(form, connection_id):
    postgres_instance = PostgresConnection.objects.get(
        connection__id=connection_id)
    postgres_instance.db_name = form.cleaned_data["db_name"]
    postgres_instance.username = form.cleaned_data["username"]
    postgres_instance.host = form.cleaned_data["host"]
    postgres_instance.port = form.cleaned_data["port"]
    postgres_instance.save()


def edit_postgres_connection_form(postgres_connection):
    return EditPostgresConnectionForm({
        "connection_name": postgres_connection.connection.name,
        "db_name": postgres_connection.db_name,
        "username": postgres_connection.username,
        "host": postgres_connection.host,
        "port": postgres_connection.port,
        "time_out": postgres_connection.connection.time_out,
        "connection_type": postgres_connection.connection.connection_type.name
    })


def test_postgres_connection(connection_form, form):
    return test_connection(connection_form, form, postgres_connection, DatastorePostgres)


def save_postgres_connection(postgres_form, form):
    return save_connection(postgres_form, form, postgres_connection)


def save_edit_postgres_connection(form, connection_id):
    save_edit_postgres_connection_form(form, connection_id)
    save_edit_connection_form(form, connection_id)


def edit_postgres_connection(post_request=None, connection_pk=None):
    return edit_connection(EditPostgresConnectionForm,
                           edit_postgres_connection_form,
                           PostgresConnection,
                           post_request,
                           connection_pk)
