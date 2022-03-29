from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from restapi.mixins import BasicLoggingMixin


class APIRoot(BasicLoggingMixin, APIView):
    def get(self, request, format=None):
        return Response({
            "organization": reverse("organization-detail", request=request, format=format, args=[1]),
            "organization groups": reverse("organizationgroup-list", request=request, format=format),
            "connections": reverse("connection-list", request=request, format=format),
            "datasets": reverse("dataset-list", request=request, format=format),
            "dataset runs": reverse("datasetrun-list", request=request, format=format),
            "jobs": reverse("job-list", request=request, format=format),
            "job runs": reverse("jobrun-list", request=request, format=format),
            "users": reverse("user-list", request=request, format=format),
            "contacts": reverse("contact-list", request=request, format=format),
            "settings": reverse("settings-detail", request=request, format=format, args=[1]),
            "procedure": {
                "profile dataset": reverse("profile-dataset", request=request, format=format),
                "refresh data": reverse("refresh-data", request=request, format=format),
                "extract metadata": reverse("extract-metadata", request=request, format=format),
                "read data": reverse("read-data", request=request, format=format)
            }
        })
