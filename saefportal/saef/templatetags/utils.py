import os
import sys
from ..enums import MonitorStatus
from urllib.parse import urlencode
from collections import OrderedDict
from django import template
from django.utils.safestring import mark_safe

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

register = template.Library()


@register.filter
def status_color(status_type):
    if status_type == MonitorStatus.SUCCEEDED.value:
        return 'green'
    elif status_type == MonitorStatus.SUCCEEDED_ISSUE.value:
        return 'orange'
    elif status_type == MonitorStatus.FAILED.value:
        return 'red'


@register.filter
def status_icon(status_type):
    if status_type == MonitorStatus.SUCCEEDED.value:
        return 'fa fa-check-circle'
    elif status_type == MonitorStatus.SUCCEEDED_ISSUE.value:
        return 'fa fa-exclamation-circle'
    elif status_type == MonitorStatus.FAILED.value:
        return 'fa fa-times-circle'


@register.simple_tag
def sort_direction(request, column):
    """
    Checks the url and depending on the selected orderby filter returns a icon that displays
    visually if it sorted by 'descending' or 'ascending' order
    """
    dict_ = request.GET.copy()

    if 'order_by' in dict_.keys():
        if dict_['order_by'].startswith('-') and dict_['order_by'].lstrip('-') == column:
            return mark_safe('<i class="fa fa-arrow-down"></i>')
        elif dict_['order_by'] == column:
            return mark_safe('<i class="fa fa-arrow-up"></i>')
    elif column == 'name':
        return mark_safe('<i class="fa fa-arrow-up"></i>')

    return mark_safe('<i></i>')


@register.simple_tag
def url_append(request, field, value, direction=''):
    """
    Append multiple fields in url to allow for multiple variables
    If field is orderby, then first time you click it will sort in 'descending' order,
    if you click the same field again it will revert to 'ascending' order.
    """
    dict_ = request.GET.copy()

    if field == 'order_by' and field in dict_.keys():
        if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
            dict_[field] = value
        elif dict_[field].lstrip('-') == value:
            dict_[field] = "-" + value
        else:
            dict_[field] = direction + value
    else:
        dict_[field] = direction + value

    return urlencode(OrderedDict(sorted(dict_.items())))



@register.filter
def lookup_bool(value, dictionary):
    if value in dictionary:
        if dictionary[value] == 'true':
            return True
    return False

@register.filter
def next_item(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) + 1]  # access the next element
    except:
        return ''  # return empty string in case of exception


@register.filter
def previous_item(some_list, current_index):
    """
    Returns the previous element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) - 1]  # access the previous element
    except:
        return ''  # return empty string in case of exception


@register.filter
def get_item(item_list, index):
    return item_list[index]


@register.filter
def get_dict(dictionary, key):
    return dictionary.get(key)
