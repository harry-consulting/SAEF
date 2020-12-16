""" views for the restapi """
from __future__ import absolute_import, unicode_literals

from rest_framework import permissions, viewsets

from saef.models import Application, JobSessionStatus, DatasetProfileHistory, ColumnProfileHistory
from ..serializers import ApplicationSerializer, JobSessionStatusSerializer, DatasetProfileHistorySerializer, \
    ColumnProfileHistorySerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]


class JobSessionStatusViewSet(viewsets.ModelViewSet):
    queryset = JobSessionStatus.objects.all()
    serializer_class = JobSessionStatusSerializer
    permission_classes = [permissions.IsAuthenticated]


class DatasetProfileHistoryViewSet(viewsets.ModelViewSet):
    queryset = DatasetProfileHistory.objects.all()
    serializer_class = DatasetProfileHistorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ColumnProfileHistoryViewSet(viewsets.ModelViewSet):
    queryset = ColumnProfileHistory.objects.all()
    serializer_class = ColumnProfileHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
