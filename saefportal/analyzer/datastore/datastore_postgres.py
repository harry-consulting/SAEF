import psycopg2
from analyzer.utilities import decrypt
from .datastore import Datastore


class DatastorePostgres(Datastore):
    def __init__(self, connection):
        super().__init__()
        connection_string = {
            'host':  connection.host,
            'user': connection.username,
            'password': decrypt(connection.password),
            'database': connection.db_name,
            'port': connection.port,
            'connect_timeout': connection.connection.time_out
        }
        self._connection_string = connection_string

    def execute_query(self, query):
        try:
            """ 
                example query and record parameter 
                a DDL statement or calling of a SP. 
            """
            connection = psycopg2.connect(**self._connection_string)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            return True

        except (Exception, psycopg2.DatabaseError):
            return False

        finally:
            try:
                cursor.close()
                connection.close()
            except NameError:
                pass

    def fetch_one(self, query, get_column_names=False):
        """execute a query and get one row as result"""
        record = None
        try:

            """ 
            example query can be SELECT TOP 1 col1, col2 from table1 
            """
            connection = psycopg2.connect(**self._connection_string)
            cursor = connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            if get_column_names:
                record = [desc[0] for desc in cursor.description]
        except (Exception, psycopg2.DatabaseError) as error:
            record = error

        finally:
            if (connection):
                cursor.close()
                connection.close()
            return record

    def fetch_all(self, query, get_column_names=False, timeout=None):
        records = None
        try:
            connection = psycopg2.connect(**self._connection_string)
            cursor = connection.cursor()
            if timeout:
                cursor.execute(f"SET statement_timeout = {timeout}")
            cursor.execute(query)
            records = cursor.fetchall()
            if get_column_names:
                records.insert(0, [desc[0] for desc in cursor.description])

        except (psycopg2.ProgrammingError, psycopg2.DatabaseError) as error:
            records = error

        finally:
            try:
                if connection:
                    cursor.close()
                    connection.close()
                return records
            except NameError:
                return records
