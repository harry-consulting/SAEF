from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Job, JobRun


admin.site.register(Job, SimpleHistoryAdmin)
admin.site.register(JobRun)
