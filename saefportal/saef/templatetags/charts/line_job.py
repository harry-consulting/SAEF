import json
import os
import sys

from django import template
from saef.models import Dataset, DatasetProfileHistory
from saef.util import ColorGenerator

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

register = template.Library()


@register.inclusion_tag('job/linechart_job.html')
def linechart_job(jo_id=-1, amount=5, profile_name="row count"):
    if jo_id == -1:
        return None

    labels = []
    data_list = []
    datasets = Dataset.objects.filter(job_id=jo_id)
    datasets_amount = datasets.count()
    color_generator = ColorGenerator()
    color_list = color_generator.generate(datasets_amount)
    i = 0
    for dataset in datasets:
        data = []
        profile_history = DatasetProfileHistory.objects.filter(dataset_id=dataset.id).order_by('-create_timestamp')[
                          :amount]
        color = color_list[i]
        for row in profile_history:
            if i <= 0:
                batch_time = row.create_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                labels.append(str(batch_time))

            profile = json.loads(row.profile_json)
            profile_value = profile[profile_name]
            data.append(profile_value)
        data.reverse()
        i = i + 1
        if data.__len__() > 0:
            data_list.append((dataset.dataset_name, color, data))
    labels.reverse()
    return {'labels': labels, 'data_list': data_list}
