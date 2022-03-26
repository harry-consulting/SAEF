import logging

import pandas as pd
import pyodbc
from django.db import models
from fernet_fields import EncryptedCharField

from datastores.mixins import GetConnectionMixin
from datastores.util import get_query, structure_tables_views

logger = logging.getLogger(__name__)


class AzureDatastore(GetConnectionMixin, models.Model):
    database_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    password = EncryptedCharField(max_length=128)
    host = models.CharField(max_length=300)
    port = models.IntegerField(default=1433)

    def __init__(self, *args, **kwargs):
        super(AzureDatastore, self).__init__(*args, **kwargs)
        self._connection_string = f'DRIVER={pyodbc.drivers()[-1]};SERVER={self.host};PORT={self.port};' \
                                  f'DATABASE={self.database_name};UID={self.username};' \
                                  f'PWD={self.password}'

    def __str__(self):
        return self.database_name

    def get_connection_details(self):
        return f"Database: {self.database_name}, Host: {self.host}, Port: {self.port}"

    def _execute_query(self, query, get_column_names=False, commit=False):
        try:
            connection = pyodbc.connect(self._connection_string)
            cursor = connection.cursor()

            cursor.execute(query)
            logger.info(f"Executed '{query}' on {self} (Azure).")

            if commit:
                cursor.commit()
            else:
                rows = cursor.fetchall()

                if get_column_names:
                    return rows, [col[0] for col in cursor.description]
                else:
                    return rows
        except Exception as error:
            logger.error(f"Error while executing '{query}' on {self} (Azure): {error}")

    def is_connection_valid(self):
        try:
            pyodbc.connect(self._connection_string)
            return True
        except (pyodbc.DatabaseError, pyodbc.InterfaceError):
            return False

    def get_viable_datasets(self):
        table_query = "SELECT schema_name(schema_id) as schema_name, t.name " \
                      "FROM sys.tables t " \
                      "ORDER BY schema_name;"

        view_query = "SELECT schema_name(schema_id) as schema_name, name " \
                     "FROM sys.views " \
                     "WHERE schema_name(schema_id) != 'sys'" \
                     "ORDER BY schema_name;"

        return structure_tables_views(self._execute_query(table_query), self._execute_query(view_query))

    def retrieve_data(self, dataset=None, query=None, limit=None):
        query = get_query(dataset, query)

        if "TOP" not in query and limit:
            limit_query = f" TOP {limit}"
            select_query_index = query.index("SELECT") + len("SELECT")
            query = query[:select_query_index] + limit_query + query[select_query_index:]

        data, column_names = self._execute_query(query, get_column_names=True)

        return pd.DataFrame([tuple(row) for row in data], columns=column_names)
