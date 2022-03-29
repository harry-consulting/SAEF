import logging

import pandas as pd
import psycopg2
from django.db import models
from fernet_fields import EncryptedCharField

from datastores.mixins import GetConnectionMixin
from datastores.util import get_query, structure_tables_views

logger = logging.getLogger(__name__)


class PostgresDatastore(GetConnectionMixin, models.Model):
    database_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    password = EncryptedCharField(max_length=128)
    host = models.CharField(max_length=300)
    port = models.IntegerField(default=5432)

    def __init__(self, *args, **kwargs):
        super(PostgresDatastore, self).__init__(*args, **kwargs)
        self._connection_string = {
            "host": self.host,
            "user": self.username,
            "password": self.password,
            "database": self.database_name,
            "port": self.port
        }

    def __str__(self):
        return self.database_name

    def get_connection_details(self):
        return f"Database: {self.database_name}, Host: {self.host}, Port: {self.port}"

    def _execute_query(self, query, get_column_names=False, commit=False):
        connection = cursor = None

        try:
            connection = psycopg2.connect(**self._connection_string)
            cursor = connection.cursor()

            cursor.execute(query)
            logger.info(f"Executed {query} on {self} (PostgreSQL).")

            if commit:
                connection.commit()
            else:
                rows = cursor.fetchall()

                if get_column_names:
                    return rows, [col.name for col in cursor.description]
                else:
                    return rows
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error while executing {query} on {self} (PostgreSQL): {error}")
        finally:
            if connection:
                connection.close()
            if cursor:
                cursor.close()

    def is_connection_valid(self):
        try:
            psycopg2.connect(**self._connection_string)
            return True
        except psycopg2.OperationalError:
            return False

    def get_viable_datasets(self):
        table_query = "SELECT table_schema, table_name " \
                      "FROM information_schema.tables " \
                      "WHERE table_schema != 'information_schema' AND table_schema != 'pg_catalog' " \
                      "AND table_type = 'BASE TABLE'" \
                      "ORDER BY table_schema"

        view_query = "SELECT table_schema, table_name FROM information_schema.views " \
                     "WHERE table_schema != 'information_schema' AND table_schema != 'pg_catalog' " \
                     "ORDER BY table_schema"

        return structure_tables_views(self._execute_query(table_query), self._execute_query(view_query))

    def retrieve_data(self, dataset=None, query=None, limit=None):
        query = get_query(dataset, query)

        if "LIMIT" not in query and limit:
            query = f"{query} LIMIT {limit}"

        data, column_names = self._execute_query(query, get_column_names=True)

        return pd.DataFrame(data, columns=column_names)
