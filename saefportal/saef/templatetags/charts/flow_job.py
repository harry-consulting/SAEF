import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from saef.models import Job, Dataset 
import json
import datetime


import logging

logger = logging.getLogger(__name__)


register = template.Library()

@register.inclusion_tag('job/flow_job.html')
def flow_job(jo_id = -1):
    if(jo_id == -1):
        return None

    logger.debug(' enable job flow ')
    datasets = Dataset.objects.filter(job_id = jo_id).order_by('sequence_in_job')
    job = Job.objects.filter(id = jo_id)[:1].get()
    dataset_links = []
    i=0 
    dataset_count = datasets.count()
    for dataset in datasets:
        i = i+1 
        if(i<dataset_count):
            next_dataset = datasets[i]
            dataset_links.append((dataset.dataset_name, next_dataset.dataset_name))

    return {'job': job, 'datasets': datasets, 'dataset_links': dataset_links} 