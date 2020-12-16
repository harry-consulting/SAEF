from ..filters import FilterByDaterange, FilterByOrder, FilterByStatus, FilterByApplication, FilterByJob
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import DatasetSessionMetaData


@login_required()
def dataset_overview(request):
    dataset_sessions_metadata = DatasetSessionMetaData.objects.filter()
    dataset_sessions_metadata_count = dataset_sessions_metadata.count()
    
    filter_by_status = FilterByStatus(request)
    dataset_sessions_metadata = filter_by_status.filter(dataset_sessions_metadata)

    filter_by_daterange = FilterByDaterange(request, 'dataset')
    dataset_sessions_metadata = filter_by_daterange.filter(dataset_sessions_metadata)

    filter_order_by = FilterByOrder(request, 'dataset', 
                                    application_order='dataset_session__job_session__application_session',
                                    job_order='dataset_session__job_session')
    dataset_sessions_metadata = filter_order_by.filter(dataset_sessions_metadata)
    
    filter_by_application = FilterByApplication(request, 'dataset_session__job_session__application_session')
    dataset_sessions_metadata = filter_by_application.filter(dataset_sessions_metadata)

    filter_by_job = FilterByJob(request, filter_by_application.selected)
    dataset_sessions_metadata = filter_by_job.filter(dataset_sessions_metadata)
    
    response_data = {'dataset_sessions_metadata': dataset_sessions_metadata,
                     'dataset_sessions_metadata_count': dataset_sessions_metadata_count,
                     'status_options': filter_by_status.options,
                     'status_selected': filter_by_status.selected,
                     'date_options': filter_by_daterange.options,
                     'date_selected': filter_by_daterange.selected,
                     'application_options': filter_by_application.options,
                     'application_selected': filter_by_application.selected,
                     'job_options': filter_by_job.options,
                     'job_selected': filter_by_job.selected}
    
    return render(request, 'dataset_overview/dataset_overview.html', response_data)