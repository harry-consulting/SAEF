from ..filters import FilterByColumn
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saef.models import DatasetSessionMetaData
from analyzer.models import ActualDatasetProfile, ExpectedDatasetProfile, ActualColumnProfile
from django.core.exceptions import ObjectDoesNotExist

@login_required()
def dataset_detail(request, session_pk):
    data = {}
    try:
        data['metadata'] = DatasetSessionMetaData.objects.get(pk=session_pk)
        actual_dataset_profile = ActualDatasetProfile.objects.get(dataset_session=data['metadata'].dataset_session)
        expected_dataset_profile = ExpectedDatasetProfile.objects.get(actual_dataset_profile=actual_dataset_profile)
        actual_column_profile = ActualColumnProfile.objects.filter(dataset_profile=actual_dataset_profile.pk)
        
        recent_dataset_sessions_metadata = DatasetSessionMetaData.objects\
            .filter(dataset_session__dataset=data['metadata'].dataset_session.dataset)\
            .order_by('-pk')[:10]
        
        filter_by_column = FilterByColumn(request)
        
        data['actual_dataset_profile'] = actual_dataset_profile
        data['expected_dataset_profile'] = expected_dataset_profile
        data['actual_column_profile'] = actual_column_profile
        data['selected_columns'] = filter_by_column.selected_columns
        data['recent_dataset_sessions_metadata'] = recent_dataset_sessions_metadata

        return render(request, 'dataset_overview/dataset_detail.html', data)
    except AttributeError:
        return render(request, 'dataset_overview/dataset_detail.html', data)
    except ObjectDoesNotExist:
        return render(request, 'dataset_overview/dataset_detail.html', data)
        