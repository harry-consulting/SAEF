from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from . import views

app_name = "saef"
urlpatterns = [
    path('ajax/update_notifications/', views.update_notifications, name='update_notifications')
]

urlpatterns += staticfiles_urlpatterns()
