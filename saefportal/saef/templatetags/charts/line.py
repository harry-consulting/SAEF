from django import template

register = template.Library()

@register.inclusion_tag('charts/chart_line.html')
def chart_line(session_meta_data):
    labels = []
    data = []
    for metadata in session_meta_data:
        labels.append(metadata.session_created().isoformat())
        data.append(metadata.dataset_session.degree_of_change)
        
    return {'labels': labels, 'datasets': [{'data': data, 'borderColor': "#3e95cd", 'label': "Degree of change"}]}
