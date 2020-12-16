from ..enums import MonitorStatus
from ..filters import FilterByOrder
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import ApplicationSessionMetaData, JobSessionMetaData
from django.core.exceptions import ObjectDoesNotExist

@login_required()
def application_detail(request, session_pk):
    data = {}
    
    try:
        data['metadata'] = ApplicationSessionMetaData.objects.filter(pk=session_pk).first()
        recent_application_sessions_metadata = ApplicationSessionMetaData.objects\
                                                .filter(application_session__application=data['metadata'].application_session.application)\
                                                .order_by('-pk')[:10]
                                                
        job_sessions_metadata = JobSessionMetaData.objects\
                                    .filter(job_session__application_session__pk=data['metadata'].application_session.pk)
        
        filter_order_by = FilterByOrder(request, 'job')
        job_sessions_metadata = filter_order_by.filter(job_sessions_metadata)
        
        succeeded_jobs = sum(map(lambda job :job.status_type == MonitorStatus.SUCCEEDED.value, job_sessions_metadata))
        total_jobs = job_sessions_metadata.count()
        
        data['recent_application_sessions_metadata'] = recent_application_sessions_metadata
        data['job_sessions_metadata'] = job_sessions_metadata
        data['total_jobs'] = total_jobs
        data['succeeded_jobs'] = succeeded_jobs
        
        return render(request, 'application_overview/application_detail.html', data)
    except AttributeError:
        return render(request, 'application_overview/application_detail.html', data)
    except ObjectDoesNotExist:
        return render(request, 'application_overview/application_detail.html', data)
        