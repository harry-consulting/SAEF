import os
import sys

from django import template
from saef.models import JobSession

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

register = template.Library()


@register.inclusion_tag('saef/list_operations.html')
def list_operations(app_id=-1, jo_id=-1, amount=5):
    operations = None
    if app_id == -1:
        operations = JobSession.objects.order_by('-create_timestamp')[:amount]
    else:
        if jo_id == -1:
            operations = JobSession.objects.filter(job__application_id=app_id).order_by('-create_timestamp')[:amount]
        else:
            operations = JobSession.objects.filter(job_id=jo_id).order_by('-create_timestamp')[:amount]

    return {'operations': operations}
