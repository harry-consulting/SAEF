import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from saef.models import Application, Job

register = template.Library()


@register.inclusion_tag('application/hierarchy_application.html')
def hierarchy_application(app_id=-1):
    if app_id == -1:
        return None

    jobs = Job.objects.filter(application_id=app_id)
    application = Application.objects.filter(id=app_id)[:1].get()
    return {'application': application, 'jobs': jobs}
