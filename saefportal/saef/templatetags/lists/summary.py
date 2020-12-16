import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from django.db.models import Count
from saef.models import Application, Job, Dataset

register = template.Library()

@register.inclusion_tag('saef/list_summary.html')
def list_summary(app_id = -1, jo_id=-1):
    summary = []
    if(app_id == -1):
        application_count = Application.objects.all().count()
        summary.append(("Number of Applications", application_count))
        job_count = Job.objects.all().count()
        summary.append(("Number of Jobs", job_count))
        dataset_count = Dataset.objects.all().count()
        summary.append(("Number of Datasets", dataset_count))

    else:
        if (jo_id == -1):
            dataset_count = Dataset.objects.filter(job_id = jo_id).count()
            summary.append(("Number of Related Datasets", dataset_count))
        else:
            job_count = Job.objects.filter(application_id = app_id).count()
            summary.append(("Number of Related Jobs", job_count))
            dataset_count = Dataset.objects.filter(job_id = jo_id).count()
            summary.append(("Number of Related Datasets", dataset_count))
    
    return {'summary': summary} 
    
