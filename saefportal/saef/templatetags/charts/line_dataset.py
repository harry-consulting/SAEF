""" define the linechart dataset tag  """
from __future__ import absolute_import, unicode_literals
import json

from django import template
from saef.models import DatasetProfileHistory 

register = template.Library()

@register.inclusion_tag('dataset/linechart_dataset.html')
def linechart_dataset(ds_id = -1, amount = 5, profile_name="row count"):
    if(ds_id == -1):
        return None

    data= []
    labels = [] 
    profile_history = DatasetProfileHistory.objects.filter(dataset_id = ds_id).order_by('-create_timestamp')[:amount]
    for row in profile_history:
        batch_time = row.create_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        profile = json.loads(row.profile_json)
        profile_value = profile[profile_name]
        labels.append(str(batch_time))
        data.append(profile_value)
    labels.reverse()
    data.reverse()
    return {'data': data, 'labels': labels} 
    
