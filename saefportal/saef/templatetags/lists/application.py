import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from django import template
from saef.models import Application

register = template.Library()

@register.inclusion_tag('application/list_application.html')
def list_application(app_id = -1):
    if(app_id == -1):
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(application_id = app_id)
    
    return {'applications': applications} 
    
