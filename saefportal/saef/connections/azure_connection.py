from saef.models import AzureConnection
from saef.forms import AddAzureConnectionForm, EditAzureConnectionForm
from analyzer.datastore import DatastoreAzure
from analyzer.utilities import encrypt

from .utils import create_connection, test_connection, save_connection, save_edit_connection_form, edit_connection


def azure_form_helper():
    return {'add': AddAzureConnectionForm,
            'edit': edit_azure_connection,
            'save': save_azure_connection,
            'save_edit': save_edit_azure_connection,
            'test': test_azure_connection}


def azure_connection(azure_form, form):
    connection = create_connection(azure_form, form)

    db_name = azure_form["db_name"]
    username = azure_form["username"]
    password = encrypt(azure_form["password"])
    host = azure_form["host"]
    port = azure_form["port"]

    azure_connection = AzureConnection(
        db_name=db_name,
        username=username,
        password=password,
        host=host,
        port=port,
        connection=connection
    )

    return connection, azure_connection


def save_edit_azure_connection_form(form, connection_id):
    postgres_instance = AzureConnection.objects.get(
        connection__id=connection_id)
    postgres_instance.db_name = form.cleaned_data["db_name"]
    postgres_instance.username = form.cleaned_data["username"]
    postgres_instance.host = form.cleaned_data["host"]
    postgres_instance.port = form.cleaned_data["port"]
    postgres_instance.save()


def edit_azure_connection_form(azure_connection):
    return EditAzureConnectionForm({
        "connection_name": azure_connection.connection.name,
        "db_name": azure_connection.db_name,
        "username": azure_connection.username,
        "host": azure_connection.host,
        "port": azure_connection.port,
        "time_out": azure_connection.connection.time_out,
        "connection_type": azure_connection.connection.connection_type.name
    })


def test_azure_connection(connection_form, form):
    return test_connection(connection_form, form, azure_connection, DatastoreAzure)


def save_azure_connection(azure_form, form):
    return save_connection(azure_form, form, azure_connection)


def save_edit_azure_connection(form, connection_id):
    save_edit_azure_connection_form(form, connection_id)
    save_edit_connection_form(form, connection_id)


def edit_azure_connection(post_request=None, connection_pk=None):
    return edit_connection(EditAzureConnectionForm,
                           edit_azure_connection_form,
                           AzureConnection,
                           post_request,
                           connection_pk)
