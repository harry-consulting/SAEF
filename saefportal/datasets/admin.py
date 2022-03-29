from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Connection, Dataset, DatasetRun, Note

admin.site.register(Connection)
admin.site.register(Dataset, SimpleHistoryAdmin)
admin.site.register(DatasetRun)
admin.site.register(Note)
