from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Contact, Settings

admin.site.register(Contact)
admin.site.register(Settings, SingletonModelAdmin)
