""" define the url mappings for the rest apis"""
from __future__ import absolute_import, unicode_literals

from django.urls import include, path
from rest_framework import routers
import restapi.views as views

router = routers.DefaultRouter()
router.register(r'application', views.ApplicationViewSet)
router.register(r"application_sessions", views.ApplicationSessionViewSet, "application_sessions")
router.register(r'job_sessions', views.JobSessionViewSet)
router.register(r'job_session_status', views.JobSessionStatusViewSet)
router.register(r'dataset_session', views.DatasetSessionViewSet)
router.register(r'dataset_profile_history', views.DatasetProfileHistoryViewSet)
router.register(r'column_profile_history', views.ColumnProfileHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]