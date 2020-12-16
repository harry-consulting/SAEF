from django import template
from .utils import chart_session

register = template.Library()

def session_data_method(metadata, session_ended):
    return [str(metadata.pk), 
            metadata.session_name(), 
            metadata.session_created().timestamp(),
            session_ended,
            metadata.status_type,
            metadata.dataset_session.degree_of_change]
            
@register.inclusion_tag('charts/chart_timeline.html')
def chart_timeline_sessions(session_metadata, start_only=False):
    return chart_session(session_metadata, session_data_method, start_only)