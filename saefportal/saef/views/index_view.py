from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from saef.models import ApplicationSessionMetaData, JobSessionMetaData, DatasetSessionMetaData
from saef.filters import FilterByDaterange


@login_required()
def index(request):
    unsorted_application_session_meta_data = ApplicationSessionMetaData.objects.all()
    filter_application_session = FilterByDaterange(request, "application")
    sorted_application_session_meta_data = filter_application_session.filter(unsorted_application_session_meta_data)

    unsorted_job_session_meta_data = JobSessionMetaData.objects.all()
    filter_job_session = FilterByDaterange(request, "job")
    sorted_job_session_meta_data = filter_job_session.filter(unsorted_job_session_meta_data)

    unsorted_dataset_session_meta_data = DatasetSessionMetaData.objects.all()
    filter_dataset_session = FilterByDaterange(request, "dataset")
    sorted_dataset_session_meta_data = filter_dataset_session.filter(unsorted_dataset_session_meta_data)

    date_options = filter_application_session.options
    date_selected = filter_application_session.selected

    response = {
        "application_sessions": sorted_application_session_meta_data,
        "job_sessions": sorted_job_session_meta_data,
        "dataset_sessions": sorted_dataset_session_meta_data,
        "date_options": date_options,
        "date_selected": date_selected
    }

    return render(request, 'main/index.html', response)
