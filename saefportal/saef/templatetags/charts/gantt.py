from django import template
from .utils import chart_session

register = template.Library()


def session_data_method(metadata, session_ended):
    return [metadata.session_name(), 
            metadata.session_name(), 
            metadata.status_type,
            metadata.session_created().timestamp(),
            session_ended,
            'null', 
            100, 
            'null']

@register.inclusion_tag('charts/chart_gantt.html')
def chart_gantt_sessions(session_metadata, start_only=False):
    return chart_session(session_metadata, session_data_method, start_only)