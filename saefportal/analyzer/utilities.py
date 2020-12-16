""" Utility module that includes all helper functions and CONSTs in this App """
import base64
import os
import sys
from Crypto.Cipher import AES

from saef.enums import ConnectionType
from saefportal.settings import SECRET_KEY
from saef.models import Connection, PostgresConnection, AzureConnection, AzureBlobStorageConnection

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

class Singleton(type):
    """ a Template class for defining Singleton class """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Validator:
    """ a class with different generic validation functions """

    def validate_empty_string(self, input_string):
        "check if a string is empty or has not content after trimming"
        if not input_string:
            return False

        if (input_string.strip() == ""):
            return False

        return True

def encrypt(plain_text):
    enc_secret = AES.new(SECRET_KEY[:32])
    tag_string = (str(plain_text) + (AES.block_size - len(str(plain_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))

    return cipher_text.decode("utf-8")


def decrypt(plain_text):
    dec_secret = AES.new(SECRET_KEY[:32])
    raw_decrypted = dec_secret.decrypt(base64.b64decode(plain_text))
    clear_val = raw_decrypted.decode().rstrip("\0")
    return clear_val


def connection_type(connection_pk, retrieve_recordset=True):
    connection = Connection.objects.get(pk=connection_pk)

    if connection.connection_type.name == ConnectionType.POSTGRES.value:
        if retrieve_recordset:
            from analyzer.recordset import RecordsetPostgres as Object
        else:
            from analyzer.datastore import DatastorePostgres as Object

        connection = PostgresConnection.objects.get(connection=connection_pk)
    elif connection.connection_type.name == ConnectionType.AZURE.value:
        if retrieve_recordset:
            from analyzer.recordset import RecordsetAzure as Object
        else:
            from analyzer.datastore import DatastoreAzure as Object
            
        connection = AzureConnection.objects.get(connection=connection_pk)
    elif connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
        from analyzer.recordset import RecordsetCSV as Object
        connection = AzureBlobStorageConnection.objects.get(connection=connection_pk)
    else:
        return connection, None

    return connection, Object
