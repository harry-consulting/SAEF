from django.utils import timezone
from dateutil.relativedelta import relativedelta

class FilterByDaterange():
    '''
    Filter to show specific dateranges in a session
    Requires GET request with 'date_option' argument 
    and the name of the session object, e.g application, job, dataset
    '''
    def __init__(self, request, name):
        self.request = request
        self.name = name
        self.options = self.get_options()
        self.selected = self.get_selected()
        
    def filter(self, sessions_metadata):
        daterange_filter = self.options[self.selected]['filter']
        sessions_metadata = sessions_metadata.filter(**daterange_filter)
            
        return sessions_metadata
        
    def get_selected(self):
        date_selected = 'All dates'
        
        if 'date_option' in self.request.GET and self.request.GET.get('date_option') in self.options:
            date_selected = self.request.GET.get('date_option')
        
        return date_selected

    def add_option(self, date_options, option_name, now, past):
        format_query = '%Y-%m-%d %H:%M%z'
        format_display = '%Y-%m-%d %H:%M'
        
        date_options[option_name] = {'range': '', 'filter': {}}
        
        if past:
            date_options[option_name]['range'] = (f'\t({past.strftime(format_display)} - {now.strftime(format_display)})')
            date_options[option_name]['filter'] = {f'{self.name}_session__create_timestamp__gte': past.strftime(format_query)}

    def get_options(self):
        now = timezone.now()
        past_hours_1 = (now - timezone.timedelta(hours=1))
        past_hours_2 = (now - timezone.timedelta(hours=2))
        past_hours_4 = (now - timezone.timedelta(hours=4))
        past_hours_12 = (now - timezone.timedelta(hours=12))
        past_days_1 = (now - timezone.timedelta(days=1))
        past_days_7 = (now - timezone.timedelta(days=7))
        past_days_31 = (now - relativedelta(months=1))
        
        date_options = {}
        self.add_option(date_options, 'All dates', now, None)
        self.add_option(date_options, '1 hour', now, past_hours_1)
        self.add_option(date_options, '2 hours', now, past_hours_2)
        self.add_option(date_options, '4 hours', now, past_hours_4)
        self.add_option(date_options, '12 hours', now, past_hours_12)
        self.add_option(date_options, '1 day', now, past_days_1)
        self.add_option(date_options, '7 days', now, past_days_7)
        self.add_option(date_options, '1 month', now, past_days_31)
       
        return date_options