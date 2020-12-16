from ..filters import FilterByDaterange, FilterByOrder, FilterByStatus
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import ApplicationSessionMetaData


@login_required()
def application_overview(request):
    application_sessions_metadata = ApplicationSessionMetaData.objects.filter()
    application_sessions_metadata_count = application_sessions_metadata.count()

    filter_by_status = FilterByStatus(request)
    application_sessions_metadata = filter_by_status.filter(application_sessions_metadata)

    filter_by_daterange = FilterByDaterange(request, 'application')
    application_sessions_metadata = filter_by_daterange.filter(application_sessions_metadata)

    filter_order_by = FilterByOrder(request, 'application')
    application_sessions_metadata = filter_order_by.filter(application_sessions_metadata)

    response_data = {'application_sessions_metadata': application_sessions_metadata,
                     'application_sessions_metadata_count': application_sessions_metadata_count,
                     'status_options': filter_by_status.options,
                     'status_selected': filter_by_status.selected,
                     'date_options': filter_by_daterange.options,
                     'date_selected': filter_by_daterange.selected}
    
    return render(request, 'application_overview/application_overview.html', response_data)
