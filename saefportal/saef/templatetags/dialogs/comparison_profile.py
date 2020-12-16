import json
from analyzer.models import ActualDatasetProfile, ActualColumnProfile, RatioCount, RatioColumn
from django.core import serializers
from django import template

register = template.Library()

def serialize_fields(model):
    return serializers.serialize('python', [ model, ])[0]['fields']

def format_profile(actual_dataset_profile, actual_column_profile, ratio_count, ratio_column):
    profile = {}
    profile['actual'] = serialize_fields(actual_dataset_profile)
    profile['actual']['column'] = {}
    profile['comparison'] = {}
    
    add_profile_fields(actual_column_profile, profile['actual']['column'], 'dataset_profile')
    add_profile_fields(ratio_count, profile['comparison'], 'dataset_ratio')
    add_profile_fields(ratio_column, profile['comparison'], 'dataset_ratio')
        
    return json.dumps(profile, indent=4)

def add_profile_fields(fields, profile, foregin_key):
    for field in fields:
        data = serialize_fields(field)
        name = data['name']
        data.pop('name')
        data.pop(foregin_key)
        profile[name] = data
    

@register.inclusion_tag('dialogs/dialog_comparison_profile.html')
def dialog_comparison_profile(dataset_session_pk):
    try:
        actual_dataset_profile = ActualDatasetProfile.objects.get(dataset_session=dataset_session_pk)
        actual_column_profile = ActualColumnProfile.objects.filter(dataset_profile=actual_dataset_profile.pk)
        ratio_count = RatioCount.objects.filter(dataset_ratio=actual_dataset_profile.pk)
        ratio_column = RatioColumn.objects.filter(dataset_ratio=actual_dataset_profile.pk)
        result = format_profile(actual_dataset_profile, actual_column_profile, ratio_count, ratio_column)
        
        return {'dataset_session_pk': dataset_session_pk,
                'profile': result}
    except AttributeError: 
        # Exception may appear when data has been deleted from the database
        return None