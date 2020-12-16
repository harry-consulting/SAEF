from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from saef.models import Application, JobSession, JobSessionStatus, DatasetProfileHistory, ColumnProfileHistory, ApplicationSession, DatasetSession

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'


class ApplicationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationSession
        fields = '__all__'


class ApplicationSessionStartSerializer(serializers.Serializer):
    application_name = serializers.CharField()
    application_token = serializers.UUIDField()
    status_time = serializers.DateTimeField()


class ApplicationSessionEndSerializer(serializers.Serializer):
    execution_id = serializers.UUIDField()
    status_time = serializers.DateTimeField()


class JobSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSession
        fields = '__all__'


class JobSessionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSessionStatus
        fields = '__all__'
        
class JobSessionStartSerializer(serializers.ModelSerializer):
    application_execution_id = serializers.UUIDField()
    name = serializers.CharField()
    
    class Meta:
        model = JobSession
        fields = ['application_execution_id', 'name', 'status_time']
        
class JobSessionEndSerializer(serializers.Serializer):
    job_execution_id = serializers.UUIDField()
    status_time = serializers.DateTimeField()
    
class DatasetSessionCalculateSerializer(serializers.ModelSerializer):
    job_execution_id = serializers.UUIDField()
    dataset_name = serializers.CharField()
    
    class Meta:
        model = DatasetSession
        fields = ['job_execution_id', 'dataset_name', 'status_time']
        
class DatasetSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetSession
        fields = '__all__'


class DatasetProfileHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetProfileHistory
        fields = '__all__'


class ColumnProfileHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnProfileHistory
        fields = '__all__'
