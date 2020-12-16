import uuid

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..util import validate_data
from ..serializers import DatasetSessionSerializer, DatasetSessionCalculateSerializer
from saef.models import JobSession, DatasetSession, Dataset
from saefportal.settings import MSG_ERROR_INVALID_INPUT, MSG_ERROR_MISSING_OBJECT_INPUT, MSG_ERROR_REQUIRED_INPUT
from analyzer.tasks import analyze_dataset


class DatasetSessionViewSet(viewsets.ModelViewSet):
    queryset = DatasetSession.objects.all()
    serializer_class = DatasetSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], serializer_class=DatasetSessionCalculateSerializer)
    def calculate(self, request):
        try:
            job_execution_id = validate_data('job_execution_id', request.data)
            dataset_name = validate_data('dataset_name', request.data)
            status_time = validate_data('status_time', request.data)
            job_session = JobSession.objects.get(execution_id=job_execution_id, status_type='START')
            dataset = Dataset.objects.get(dataset_name=dataset_name, job_id=job_session.job.id)
        except ObjectDoesNotExist:
            return Response({"error": MSG_ERROR_MISSING_OBJECT_INPUT("job execution id or dataset name")},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({"error": MSG_ERROR_INVALID_INPUT('UUID')}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": MSG_ERROR_REQUIRED_INPUT('job_execution_id and name')},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        execution_id = uuid.uuid4()
        dataset_session = DatasetSession.objects.create(job_session=job_session,
                                                        dataset=dataset,
                                                        status_time=status_time,
                                                        execution_id=execution_id)

        task = analyze_dataset(dataset_session_pk=dataset_session.pk)

        return Response(task, status=status.HTTP_200_OK)
