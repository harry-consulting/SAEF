import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from saef.models import Application, ApplicationSession, ApplicationToken, ApplicationSessionMetaData
from ..serializers import ApplicationSessionStartSerializer, \
    ApplicationSessionEndSerializer, ApplicationSessionSerializer
from analyzer.tasks import compute_application_session_meta_data


class ApplicationSessionViewSet(viewsets.ModelViewSet):
    queryset = ApplicationSession.objects.all()
    serializer_class = ApplicationSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], serializer_class=ApplicationSessionStartSerializer)
    def start(self, request):
        try:
            serializer = ApplicationSessionStartSerializer(data=request.data)
            if serializer.is_valid():
                application_token = ApplicationToken.objects.get(application_token=request.data["application_token"])
                application = Application.objects.get(name=request.data["application_name"],
                                                      application_token__pk=application_token.id)
            else:
                return Response({"error": "Request has an invalid format"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Invalid application token or name"}, status=status.HTTP_400_BAD_REQUEST)

        status_time = request.data["status_time"]
        status_type = "START"
        execution_id = uuid.uuid4()

        application_session = ApplicationSession(
            application=application,
            execution_id=execution_id,
            status_time=status_time,
            status_type=status_type
        )
        application_session.save()

        response_data = {"execution_id": execution_id}
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], serializer_class=ApplicationSessionEndSerializer)
    def end(self, request):
        try:
            serializer = ApplicationSessionEndSerializer(data=request.data)
            if serializer.is_valid():
                application_session_start = ApplicationSession.objects.get(execution_id=request.data["execution_id"],
                                                                           status_type="START")
            else:
                return Response({"error": "Request has an invalid format"}, status=status.HTTP_400_BAD_REQUEST)
            number_of_end_sessions = ApplicationSession.objects.filter(execution_id=request.data["execution_id"],
                                                                       status_type="END").count()
            if number_of_end_sessions > 0:
                return Response({"error": "Application session has already ended"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "Invalid execution id"}, status=status.HTTP_400_BAD_REQUEST)

        execution_id = request.data["execution_id"]
        status_time = request.data["status_time"]
        status_type = "END"

        application_session = ApplicationSession(
            application=application_session_start.application,
            execution_id=execution_id,
            status_time=status_time,
            status_type=status_type
        )
        application_session.save()

        result = compute_application_session_meta_data(application_session_start_pk=application_session_start.pk)

        return Response(result, status=status.HTTP_200_OK)
