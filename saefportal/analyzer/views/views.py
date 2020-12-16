from __future__ import absolute_import, unicode_literals
import json
from celery.result import AsyncResult
from django.http import HttpResponse
from django.views import generic
from saef.models import Dataset
from saef.models import JobSession, DatasetProfileHistory, ColumnProfileHistory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'analyzer/analyze.html'
    model = Dataset


@login_required()
def get_task_info(request):
    if 'task_id' in request.GET:
        task_id = request.GET['task_id']
    else:
        return HttpResponse('task id is not available.')

    task = AsyncResult(task_id)
    data = {
        'state': task.state,
        'result': task.result,
    }
    if task.status == 'SUCCESS':
        return_value = task.get()
        data = {
            'state': task.state,
            'result': task.result,
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required()
def get_dataset_result(request):
    if 'request_id' in request.GET and 'dataset_id' in request.GET:
        request_id = request.GET['request_id']
        dataset_id = request.GET['dataset_id']
    else:
        return HttpResponse('request_id or dataset_id is not avalable.')

    dataset = Dataset.objects.get(pk=dataset_id)
    job_session = JobSession.objects.get(request_id=request_id)
    dataset_profile = DatasetProfileHistory.objects.get(job_session=job_session)
    column_profile = ColumnProfileHistory.objects.filter(job_session=job_session)
    data = {'dataset name': dataset.dataset_name}
    profile = json.loads(dataset_profile.profile_json)

    for key, value in profile.items():
        data.update({str(key): str(value)})

    for row in column_profile:
        column_name = row.column_name
        parsed_json = json.loads(row.profile_json)
        data.update({'column name: ' + row.column_name: parsed_json})

    return HttpResponse(json.dumps(dict(data)), content_type='application/json')
