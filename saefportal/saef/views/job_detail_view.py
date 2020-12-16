from ..enums import MonitorStatus
from ..filters import FilterByOrder
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import JobSessionMetaData, DatasetSessionMetaData
from django.core.exceptions import ObjectDoesNotExist

@login_required()
def job_detail(request, session_pk):
    data = {}
    try:
        data['metadata'] = JobSessionMetaData.objects.get(pk=session_pk)
        recent_job_sessions_metadata = JobSessionMetaData.objects\
                                        .filter(job_session__job=data['metadata'].job_session.job)\
                                        .order_by('-pk')[:10]
                                        
        dataset_sessions_metadata = DatasetSessionMetaData.objects.filter(dataset_session__job_session__pk=data['metadata'].job_session.pk)
        
        filter_order_by = FilterByOrder(request, 'dataset')
        dataset_sessions_metadata = filter_order_by.filter(dataset_sessions_metadata)
        
        succeeded_datasets = sum(map(lambda job :job.status_type == MonitorStatus.SUCCEEDED.value, dataset_sessions_metadata))
        total_datasets = dataset_sessions_metadata.count()
        
        data['recent_job_sessions_metadata'] = recent_job_sessions_metadata
        data['dataset_sessions_metadata'] = dataset_sessions_metadata
        data['selected_comparison_result'] = request.GET.get('result')
        data['succeeded_datasets'] = succeeded_datasets
        data['total_datasets'] = total_datasets
        
        return render(request, 'job_overview/job_detail.html', data)
    except AttributeError:
        return render(request, 'job_overview/job_detail.html', data)
    except ObjectDoesNotExist:
        return render(request, 'job_overview/job_detail.html', data)
        