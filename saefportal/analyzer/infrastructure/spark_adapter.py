"""
    This module includes class that read data sources using Spark. 
    The datasource is read from various source types, such as CSV, Json, etc. 
    The output is a spark dataframe. 
"""
from __future__ import absolute_import, unicode_literals

import pyodbc
import pandas as pd

from analyzer.utilities import Singleton
from pyspark.sql import SparkSession


class GetSpark(metaclass=Singleton):
    def __init__(self, appName='saef'):
        self._appName = appName

    def get_spark_context(self):
        spark = SparkSession \
            .builder \
            .appName(self._appName) \
            .config("spark.jars") \
            .getOrCreate()
        return spark


class SparkCSVAdapter:
    def __init__(self):
        self._option_header = True
        self._option_delimiter = ','
        self._option_infer_schema = True
        self._option_encoding = 'utf8'

    def read(self, spark, file, options):
        df = spark.read.format('com.databricks.spark.csv') \
            .option('header', options.get('header', self._option_header)) \
            .option('delimiter', options.get('delimiter', self._option_delimiter)) \
            .option('inferSchema', options.get('inferSchema', self._option_infer_schema)) \
            .option('encoding', options.get('encoding', self._option_encoding)) \
            .load(file)
        return df


class SparkMSSQLAdapter:
    def __init__(self, server='localhost', port=1433, database=None, username=None, password=None):
        drivers = [item for item in pyodbc.drivers()]
        connection_string = "DRIVER=" + drivers[-1] + ";" + "SERVER=" + server + ";" + str(port) + ";" + "DATABASE=" + database + ";" + "UID=" + username + ";" + "PWD=" + password
        self.connection = pyodbc.connect(connection_string)

    def readTable(self, spark, table_name):
        sql_query = "select * from " + table_name
        pdf = pd.read_sql(sql_query, self.connection)
        return spark.createDataFrame(pdf)

    def readQuery(self, spark, query):
        pdf = pd.read_sql(query, self.connection)
        return spark.createDataFrame(pdf)

    def write(self, df, url, mode, table, properties):
        df.write.jdbc(url=url, table=table, mode=mode, properties=properties)
