from django import template
from analyzer.models import ActualColumnProfile, ExpectedColumnProfile
register = template.Library()

@register.inclusion_tag('tables/table_column_profile.html')
def table_column_profile(column_name, actual_dataset_pk):
    actual_column_profile = ActualColumnProfile.objects.filter(dataset_profile=actual_dataset_pk, name=column_name).first()
    
    expected_column_profile = ExpectedColumnProfile.objects\
                                .filter(dataset_profile__actual_dataset_profile=actual_column_profile.dataset_profile, name=column_name).first()
    return {'actual_column_profile': actual_column_profile, 'expected_column_profile': expected_column_profile}
