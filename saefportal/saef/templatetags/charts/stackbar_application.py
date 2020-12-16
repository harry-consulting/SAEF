import json
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from saef.models import Job, Dataset, DatasetProfileHistory 
from saef.util import ColorGenerator

register = template.Library()


@register.inclusion_tag('saef/stackbar_application.html')
def stackbar_application(app_id=-1, amount=5, profile_name="row count"):
    if app_id == -1:
        return None

    labels = []
    data_list = []
    jobs = Job.objects.filter(application_id=app_id)
    datasets_amount = 0
    for job in jobs:
        datasets = Dataset.objects.filter(job_id=job.id)
        for dataset in datasets:
            datasets_amount = datasets_amount + 1

    color_generator = ColorGenerator()
    color_list = color_generator.generate(datasets_amount)
    i = 0
    for job in jobs:
        job_data = []
        datasets = Dataset.objects.filter(job_id=job.id)

        for dataset in datasets:
            dataset_data = []
            profile_history = DatasetProfileHistory.objects.filter(dataset_id=dataset.id).order_by('-create_timestamp')[
                              :amount]
            color = color_list[i]

            for row in profile_history:
                if i <= 0:
                    batch_time = row.create_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    labels.append(str(batch_time))

                profile = json.loads(row.profile_json)
                profile_value = profile[profile_name]
                dataset_data.append(profile_value)

            dataset_data.reverse()
            if dataset_data.__len__() > 0:
                job_data.append((dataset.dataset_name, color, dataset_data))

            i = i + 1
        if job_data.__len__() > 0:
            data_list.append((job.name, job_data))

    labels.reverse()
    return {'labels': labels, 'data_list': data_list}
