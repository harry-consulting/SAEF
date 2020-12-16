import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from saef.models import Application, Job, Dataset, DatasetMetadataColumn, DatasetMetadataConstraint

register = template.Library()


@register.inclusion_tag('dataset/list_dataset_detail.html')
def list_dataset_detail(ds_id=-1):
    if (ds_id == -1):
        return None
    else:
        names = []
        dataset = Dataset.objects.filter(id=ds_id)[:1].get()
        names.append(("Dataset Name", dataset.dataset_name))
        job = Job.objects.filter(id = dataset.job_id)[:1].get()
        names.append(("Job Name", job.name))
        application = Application.objects.filter(id = job.application_id)[:1].get()
        names.append(("Application Name", application.name))
        dataset_metadata_column = DatasetMetadataColumn.objects.filter(dataset_id=ds_id)
        dataset_metadata_constraint = DatasetMetadataConstraint.objects.filter(dataset_id=ds_id)
        return {'names': names, 'dataset_metadata_column': dataset_metadata_column,
                'dataset_metadata_constraint': dataset_metadata_constraint}
