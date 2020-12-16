import pyodbc
from analyzer.utilities import decrypt
from .datastore import Datastore


class DatastoreAzure(Datastore):
    def __init__(self, connection):
        super().__init__()
        drivers = [item for item in pyodbc.drivers()]
        self._connection_string = f'DRIVER={drivers[-1]};SERVER={connection.host};PORT={connection.port};DATABASE={connection.db_name};UID={connection.username};PWD={decrypt(connection.password)}'

    def execute_query(self, query):
        try:
            connection = pyodbc.connect(self._connection_string)
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.commit()
            return True
        except Exception as error:
            return False

    def fetch_one(self, query, get_column_names=False):
        try:
            connection = pyodbc.connect(self._connection_string)
            cursor = connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            if get_column_names:
                record = [column[0] for column in cursor.description]
        except Exception as error:
            record = error

        return record

    def fetch_all(self, query, get_column_names=False, timeout=None):
        try:
            connection = pyodbc.connect(self._connection_string)
            cursor = connection.cursor()
            cursor.execute(query)

            records = []
            if get_column_names:
                records.append([column[0] for column in cursor.description])
            record = cursor.fetchone()
            while record:
                records.append(tuple(record))
                record = cursor.fetchone()
        except Exception as error:
            records = error

        return records
