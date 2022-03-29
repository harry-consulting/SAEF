from pyspark.sql import SparkSession
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from analyzer.tasks import run_task
from util.data_util import get_data
from datasets.models import Dataset
from restapi import serializers
from restapi.mixins import BasicLoggingMixin


class GenericProcedureAPIView(BasicLoggingMixin, GenericAPIView):
    """Generic view to support common structure of procedure views."""
    def get(self, request, **kwargs):
        return Response(kwargs["data"] if "data" in kwargs else {})

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return self.get(request, data=self.procedure(request.user.email, **serializer.data))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDataset(GenericProcedureAPIView):
    serializer_class = serializers.ProfileDatasetSerializer
    procedure = lambda *args, **kwargs: run_task("Profile dataset", args[1], kwargs)


class RefreshData(GenericProcedureAPIView):
    serializer_class = serializers.RefreshDataSerializer
    procedure = lambda *args, **kwargs: run_task("Refresh data", args[1], kwargs)


class ExtractMetadata(GenericProcedureAPIView):
    serializer_class = serializers.ExtractMetadataSerializer
    procedure = lambda *args, **kwargs: run_task("Extract metadata", args[1], kwargs)


class ReadData(GenericProcedureAPIView):
    serializer_class = serializers.ReadDataSerializer
    procedure = lambda *args, **kwargs: get_data_response(**kwargs)


def get_data_response(dataset_key, sql_query=None):
    """Query the given connection with the given query and return a formatted dict response."""
    # Use the given dataset key to retrieve a connection that can be used to access any supported database type.
    dataset = Dataset.objects.get(key=dataset_key)
    data_df = get_data(dataset)

    if sql_query:
        # Create a PySpark SparkSession.
        spark = SparkSession.builder.master("local[1]").appName("SAEF").getOrCreate()

        # Convert the pandas dataframe to a spark dataframe and run the given SQL query.
        spark_df = spark.createDataFrame(data_df)
        spark_df.createOrReplaceTempView("dataset")
        sql_df = spark.sql(sql_query)

        data_df = sql_df.toPandas()

    response = {"SQL query": sql_query, "column_names": list(data_df), "value": data_df.to_dict('records')}

    return response
