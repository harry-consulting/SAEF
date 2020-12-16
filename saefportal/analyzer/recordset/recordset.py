class Recordset:
    def __init__(self, connection_detail):
        self._connection_string = connection_detail

    def validate_query(self):
        raise NotImplementedError

    def get_column_names(self) -> list:
        raise NotImplementedError

    def get_row_count(self) -> int:
        raise NotImplementedError

    def get_column_count(self) -> int:
        raise NotImplementedError

    def get_column_types(self):
        raise NotImplementedError

    def get_column_distinct(self, column_name: str) -> list:
        raise NotImplementedError

    def get_column_min(self, column_name: str):
        raise NotImplementedError

    def get_column_max(self, column_name: str):
        raise NotImplementedError

    def get_all_tables(self):
        raise NotImplementedError

    def get_pk_and_unique_constraints(self, table):
        raise NotImplementedError

    def get_check_constraints(self, table):
        raise NotImplementedError

    def get_is_nullable_constraints(self, table):
        raise NotImplementedError

    def extract_preview(self, timeout):
        raise NotImplementedError

    def extract_schema(self, schema, table):
        raise NotImplementedError