from ..filters import FilterByDaterange, FilterByOrder, FilterByStatus, FilterByApplication
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import JobSessionMetaData


@login_required()
def job_overview(request):
    job_sessions_metadata = JobSessionMetaData.objects.filter()
    job_sessions_metadata_count = job_sessions_metadata.count()
    
    filter_by_status = FilterByStatus(request)
    job_sessions_metadata = filter_by_status.filter(job_sessions_metadata)

    filter_by_daterange = FilterByDaterange(request, 'job')
    job_sessions_metadata = filter_by_daterange.filter(job_sessions_metadata)

    filter_order_by = FilterByOrder(request, 'job', application_order='job_session__application_session')
    job_sessions_metadata = filter_order_by.filter(job_sessions_metadata)
    
    filter_by_application = FilterByApplication(request, 'job_session__application_session')
    job_sessions_metadata = filter_by_application.filter(job_sessions_metadata)

    response_data = {'job_sessions_metadata': job_sessions_metadata,
                     'job_sessions_metadata_count': job_sessions_metadata_count,
                     'status_options': filter_by_status.options,
                     'status_selected': filter_by_status.selected,
                     'date_options': filter_by_daterange.options,
                     'date_selected': filter_by_daterange.selected,
                     'application_options': filter_by_application.options,
                     'application_selected': filter_by_application.selected}
    
    return render(request, 'job_overview/job_overview.html', response_data)


