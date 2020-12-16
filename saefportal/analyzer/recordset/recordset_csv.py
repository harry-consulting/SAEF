from __future__ import absolute_import, unicode_literals

import os
from pathlib import Path

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobClient
from analyzer.infrastructure import SparkCSVAdapter, GetSpark
from pyspark.sql.utils import AnalysisException, ParseException
from saefportal.settings import SQL_QUERY_DEFAULT_LIMIT
from .recordset import Recordset

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def download_csv_file(blob_service, destination_location):
    try:
        with open(destination_location, "wb") as output_file:
            blob_data = blob_service.download_blob()
            blob_data.readinto(output_file)
    except ResourceNotFoundError as e:
        raise e


class RecordsetCSV(Recordset):
    def __init__(self, parameters, query):
        connection = parameters["connection"]
        super().__init__(connection)
        destination_location = os.path.join(CURRENT_DIR.parent.parent, "temp_resources", "temp.csv")
        try:
            blob_service = BlobClient.from_connection_string(conn_str=connection.connection_string,
                                                             container_name=connection.container_name,
                                                             blob_name=connection.blob_name)
            download_csv_file(blob_service, destination_location)
        except ResourceNotFoundError as e:
            raise e
        except ValueError as e:
            raise e
        spark_csv_adapter = SparkCSVAdapter()
        self._spark = GetSpark(appName='SAEF').get_spark_context()
        self._dataframe = spark_csv_adapter.read(self._spark, destination_location, {})
        self._dataset = parameters["dataset"]
        self._connection = connection
        self._query = query

    def validate_query(self):
        try:
            self._dataframe.createOrReplaceTempView(self._dataset.dataset_name)
            sqlDf = self._spark.sql(self._query)
            return sqlDf, True
        except AnalysisException:
            return None, False

    def get_column_names(self) -> list:
        column_names = []
        columns = self._dataframe.dtypes
        for column in columns:
            column_names.append(column[0])
        return column_names

    def get_row_count(self) -> int:
        return self._dataframe.count()

    def get_column_count(self) -> int:
        return len(self._dataframe.columns)

    def get_column_type(self, column_name: str) -> str:
        columns = self._dataframe.dtypes
        column_type = None
        for column in columns:
            if column[0] == column_name:
                column_type = column[1]
                break

        return column_type

    def get_column_distinct(self, column_name: str) -> list:
        column = self._dataframe.select(column_name).distinct()
        return list(column.select(column_name).toPandas()[column_name])

    def get_column_min(self, column_name: str):
        return self._dataframe.agg({column_name: "min"}).collect()[0][0]

    def get_column_max(self, column_name: str):
        return self._dataframe.agg({column_name: "max"}).collect()[0][0]

    def get_all_tables(self):
        return [(self._connection.container_name, self._connection.blob_name)]

    def get_column_types(self):
        return self._dataframe.dtypes

    def get_pk_and_unique_constraints(self, table):
        raise NotImplementedError

    def get_check_constraints(self, table):
        raise NotImplementedError

    def get_is_nullable_constraints(self, table):
        raise NotImplementedError

    def extract_preview(self, timeout):
        query = self._query.replace(';', '')
        if 'LIMIT' not in query:
            query = f'{query} LIMIT {SQL_QUERY_DEFAULT_LIMIT}'

        try:
            self._dataframe.createOrReplaceTempView(self._dataset.dataset_name)
            df = self._spark.sql(query)
        except ParseException as e:
            return e
        except AnalysisException as e:
            return e

        result = [df.columns]
        list_of_row_tuples = tuple(map(lambda x: tuple(x.asDict().values()), df.collect()))
        for row_tuple in list_of_row_tuples:
            result.append(row_tuple)

        return result

    def extract_schema(self, schema, table):
        return self.get_column_types()
