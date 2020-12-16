import uuid

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..util import calculate_execution_time, calculate_expected_time, validate_data
from ..serializers import JobSessionSerializer, JobSessionStartSerializer, JobSessionEndSerializer
from analyzer.tasks import compute_job_session_meta_data
from saef.models import JobSession, ApplicationSession, Job
from saefportal.settings import MSG_ERROR_INVALID_INPUT, MSG_ERROR_REQUIRED_INPUT, MSG_ERROR_MISSING_OBJECT_INPUT, \
    MSG_ERROR_EXISTING


class JobSessionViewSet(viewsets.ModelViewSet):
    queryset = JobSession.objects.all()
    serializer_class = JobSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], serializer_class=JobSessionStartSerializer)
    def start(self, request):
        try:
            application_execution_id = validate_data('application_execution_id', request.data)
            name = validate_data('name', request.data)
            status_time = validate_data('status_time', request.data)

            application_session = ApplicationSession.objects.get(execution_id=application_execution_id,
                                                                 status_type='START')
            job = Job.objects.get(name=name, application_id=application_session.application_id)

            status_type = 'START'

        except ObjectDoesNotExist:
            return Response({"error": MSG_ERROR_MISSING_OBJECT_INPUT("application execution id or job name")},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({"error": MSG_ERROR_INVALID_INPUT('UUID')}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": MSG_ERROR_REQUIRED_INPUT('application_execution_id and job_execution_id')},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        execution_id = uuid.uuid4()
        JobSession.objects.create(application_session=application_session,
                                  job=job,
                                  status_time=status_time,
                                  status_type=status_type,
                                  execution_id=execution_id)

        response_data = {"execution_id": execution_id}
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], serializer_class=JobSessionEndSerializer)
    def end(self, request):
        try:
            job_execution_id = validate_data('job_execution_id', request.data)
            status_time = validate_data('status_time', request.data)

            job_session_start = JobSession.objects.get(execution_id=job_execution_id, status_type='START')

            status_type = 'END'
            jobsession_stop = JobSession.objects.filter(execution_id=job_execution_id, status_type=status_type).count()

            if jobsession_stop > 0:
                raise Exception(MSG_ERROR_EXISTING('job', status_type))

        except ObjectDoesNotExist:
            return Response({"error": MSG_ERROR_MISSING_OBJECT_INPUT("application or job execution id")},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({"error": MSG_ERROR_INVALID_INPUT('UUID')}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": MSG_ERROR_REQUIRED_INPUT('application_execution_id and job_execution_id')},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        JobSession.objects.create(application_session=job_session_start.application_session,
                                  job=job_session_start.job,
                                  status_time=status_time,
                                  status_type=status_type,
                                  execution_id=job_execution_id)

        result = compute_job_session_meta_data(application_session_start_pk=job_session_start.pk)

        return Response(result, status=status.HTTP_200_OK)

    def validate_data(self, name, data):
        if name in data and data[name] != '':
            return data[name]
        else:
            raise Exception(MSG_ERROR_REQUIRED_INPUT('application_execution_id and job_execution_id'))
