import pyodbc
from .recordset import Recordset
from analyzer.datastore import DatastoreAzure
from saefportal.settings import SQL_QUERY_DEFAULT_LIMIT


class RecordsetAzure(Recordset):
    def __init__(self, connection_detail, query):
        super().__init__(connection_detail)
        self._datastore = DatastoreAzure(connection_detail)
        self._query = query

    def validate_query(self):
        result = self._datastore.fetch_one(self._query)
        valid = type(result) is pyodbc.Row
        return valid, result

    def get_column_names(self):
        return self._datastore.fetch_one(self._query, get_column_names=True)

    def get_row_count(self):
        query = f"SELECT count(*) as row_count from ({self._query}) AS a "
        return int(self._datastore.fetch_one(query)[0])

    def get_column_count(self):
        return len(self.get_column_names())

    def get_column_types(self):
        self._datastore.execute_query(
            f"create view dbo.tmp_1 as {self._query}")
        result = self._datastore.fetch_all(f"""
                                    SELECT Column_Name, Data_Type 
                                    from INFORMATION_SCHEMA.COLUMNS
                                    where TABLE_SCHEMA = 'dbo'
                                    AND TABLE_NAME = 'tmp_1'
                                    """)
        self._datastore.execute_query(f"DROP VIEW dbo.tmp_1")

        return result

    def get_column_distinct(self, column_name):
        query = f'SELECT distinct a."{column_name}" as value from ({self._query}) AS a;'
        column_distinct = [row[0]
                           for row in list(self._datastore.fetch_all(query))]
        return column_distinct

    def get_column_min(self, column_name):
        query = f'SELECT TOP 1 min(a."{column_name}") as type from ({self._query}) AS a'
        return self._datastore.fetch_one(query)[0]

    def get_column_max(self, column_name):
        query = f'SELECT TOP 1 max(a."{column_name}") as type from ({self._query}) AS a'
        return self._datastore.fetch_one(query)[0]

    def get_all_tables(self):
        query = "SELECT table_schema, table_name FROM information_schema.tables " + \
                "WHERE table_schema != 'information_schema'AND table_schema != 'pg_catalog' ORDER BY table_schema"

        return self._datastore.fetch_all(query)

    def get_pk_and_unique_constraints(self, table):
        query = """
            SELECT table_constraint.constraint_name, column_usage.column_name, constraint_type 
            FROM information_schema.table_constraints AS table_constraint 
            JOIN information_schema.constraint_column_usage AS column_usage 
            ON table_constraint.constraint_name = column_usage.constraint_name 
            WHERE table_constraint.table_name = '{0}'
            AND (constraint_type = 'PRIMARY KEY' OR constraint_type = 'UNIQUE'); 
            """.format(table)
        return self._datastore.fetch_all(query)

    def get_check_constraints(self, table):
        query = """
            SELECT columns.constraint_name, columns.column_name, constraints.check_clause
            FROM information_schema.constraint_column_usage AS columns
            JOIN information_schema.check_constraints AS constraints
            ON columns.constraint_name = constraints.constraint_name
            AND columns.constraint_schema = constraints.constraint_schema
            WHERE table_name = '{0}';
            """.format(table)
        return self._datastore.fetch_all(query)

    def get_is_nullable_constraints(self, table):
        query = """
            SELECT columns.column_name, columns.is_nullable
            FROM information_schema.columns AS columns
            WHERE table_name = '{0}';
            """.format(table)
        return self._datastore.fetch_all(query)

    def extract_preview(self, timeout):
        query = self._query.replace(';', '')
        if 'TOP' not in query:
            limit_query = f' TOP {SQL_QUERY_DEFAULT_LIMIT}'
            select_query_index = query.index('SELECT') + len('SELECT')
            query = query[:select_query_index] + limit_query + query[select_query_index:]
            
        return self._datastore.fetch_all(query, get_column_names=True, timeout=timeout)

    def extract_schema(self, schema, table):
        query = "SELECT column_name, data_type, is_nullable " + \
                f"FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{table}'"
        return self._datastore.fetch_all(query)
