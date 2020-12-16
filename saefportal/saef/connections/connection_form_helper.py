from saef.enums import ConnectionType
from .azure_blob_storage_connection import azure_blob_storage_form_helper
from .postgres_connection import postgres_form_helper
from .azure_connection import azure_form_helper


class ConnectionFormHelper:
    def __init__(self):
        self.connection_form = {ConnectionType.POSTGRES.value: postgres_form_helper(),
                                ConnectionType.AZURE.value: azure_form_helper(),
                                ConnectionType.AZURE_BLOB_STORAGE.value: azure_blob_storage_form_helper()}

    def lookup_connection(self, connection_type, change):
        return self.connection_form[connection_type][change]
