from saef.models import AzureBlobStorageConnection
from .utils import create_connection, save_connection, edit_connection, save_edit_connection_form
from saef.forms import AddAzureBlobStorageConnectionForm, EditAzureBlobStorageConnectionForm


def azure_blob_storage_form_helper():
    return {'add': AddAzureBlobStorageConnectionForm,
            'edit': edit_azure_blob_storage_connection,
            'save': save_azure_blob_storage_connection,
            'save_edit': save_edit_azure_blob_storage_connection}


def create_azure_blob_storage_connection(azure_blob_storage_form, connection_type_form):
    connection = create_connection(azure_blob_storage_form, connection_type_form)
    azure_blob_storage_connection = AzureBlobStorageConnection(
        connection_string=azure_blob_storage_form["connection_string"],
        container_name=azure_blob_storage_form["container_name"],
        blob_name=azure_blob_storage_form["blob_name"],
        connection=connection
    )

    return connection, azure_blob_storage_connection


def edit_azure_blob_storage_connection_form(azure_blob_storage_connection):
    return EditAzureBlobStorageConnectionForm({
        "connection_type": azure_blob_storage_connection.connection.connection_type,
        "connection_name": azure_blob_storage_connection.connection.name,
        "connection_string": azure_blob_storage_connection.connection_string,
        "container_name": azure_blob_storage_connection.container_name,
        "blob_name": azure_blob_storage_connection.blob_name,
        "time_out": azure_blob_storage_connection.connection.time_out
    })


def save_azure_blob_storage_connection(azure_blob_storage_form, form):
    return save_connection(azure_blob_storage_form, form, create_azure_blob_storage_connection)


def edit_azure_blob_storage_connection(post_request=None, connection_pk=None):
    return edit_connection(EditAzureBlobStorageConnectionForm,
                           edit_azure_blob_storage_connection_form,
                           AzureBlobStorageConnection,
                           post_request,
                           connection_pk)


def save_edit_azure_blob_storage_connection_form(form, connection_id):
    azure_blob_storage_connection_instance = AzureBlobStorageConnection.objects.get(connection__id=connection_id)
    azure_blob_storage_connection_instance.connection_string = form.cleaned_data["connection_string"]
    azure_blob_storage_connection_instance.container_name = form.cleaned_data["container_name"]
    azure_blob_storage_connection_instance.blob_name = form.cleaned_data["blob_name"]
    azure_blob_storage_connection_instance.save()


def save_edit_azure_blob_storage_connection(form, connection_id):
    save_edit_azure_blob_storage_connection_form(form, connection_id)
    save_edit_connection_form(form, connection_id)
