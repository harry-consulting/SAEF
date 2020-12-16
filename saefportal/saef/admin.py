from django.contrib import admin

# Register your models here.

from .models import ApplicationToken, Application, ConnectionType, Connection, Dataset, Job, DatasetMetadataColumn, DatasetMetadataConstraint, DatasetProfileHistory, DatasetProfileOperationHistory, PostgresConnection, JobSession

admin.site.register(ApplicationToken)
admin.site.register(Application)
admin.site.register(ConnectionType)
admin.site.register(Connection)
admin.site.register(Dataset)
admin.site.register(Job)
admin.site.register(DatasetMetadataColumn)
admin.site.register(DatasetMetadataConstraint)
admin.site.register(DatasetProfileHistory)
admin.site.register(PostgresConnection)
admin.site.register(JobSession)

