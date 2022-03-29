import os
import re
import logging

from decouple import config
from django.db import models
from pyspark.sql import SparkSession

from datastores.mixins import GetConnectionMixin
from datastores.util import convert_to_dataframe

# Set PySpark environments.
os.environ["PYSPARK_PYTHON"] = config("PYSPARK_PYTHON")
os.environ["PYSPARK_DRIVER_PYTHON"] = config("PYSPARK_DRIVER_PYTHON")

logger = logging.getLogger(__name__)


class FileDatastore(GetConnectionMixin, models.Model):
    """
    Abstract base class used to define common functionality between datastores that use files (not relational). All file
    datastores should have a "_download_data" function that returns a bytes buffer with the data and the file type.
    """
    def _apply_sql_to_dataframe(self, query, df):
        # Create a PySpark SparkSession.
        spark = SparkSession.builder.appName("SAEF").getOrCreate()

        # Convert the pandas dataframe to a spark dataframe and run the given SQL query.
        spark_df = spark.createDataFrame(df)
        spark_df.createOrReplaceTempView("dataset")

        # Modify the query to be "FROM dataset" instead of "FROM `file_id`" to avoid issues with ID formats.
        sql_df = spark.sql(query.replace(re.search("`(.+?)`", query).group(1), "dataset"))
        return sql_df.toPandas()

    def _download_as_df(self, dataset, query):
        """Download the data as a pandas dataframe. Also applies a PySpark SQL query to the data if necessary."""
        query = query if query else dataset.query
        file_id = dataset.file_id if dataset else re.search("`(.+?)`", query).group(1)

        data, file_type = self._download_data(file_id)
        logger.info(f"Downloaded '{file_id}' from {self}.")

        initial_df = convert_to_dataframe(file_type, data)
        return self._apply_sql_to_dataframe(query, initial_df) if query else initial_df

    def retrieve_data(self, dataset=None, query=None, limit=None):
        df = self._download_as_df(dataset, query)

        return df.head(limit) if limit else df

    class Meta:
        abstract = True
