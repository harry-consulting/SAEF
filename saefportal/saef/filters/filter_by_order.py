class FilterByOrder():
    '''
    Filter to order query list in specific order
    Requires GET request with 'order_by' argument 
    and the name of the session object, e.g application, job, dataset
    Optional arguments is application and job order, e.g 'job_session__application_session'
    '''
    def __init__(self, request, name, application_order=None, job_order=None):
        self.request = request
        self.name = name
        self.application_order = application_order
        self.job_order = job_order
        self.options = self.get_options()
        self.selected = self.get_selected()
        
    def filter(self, sessions_metadata):
        if self.selected:
            order_filter = self.options[self.selected]
            sessions_metadata = sessions_metadata.order_by(*order_filter)
                
        return sessions_metadata

    def get_selected(self):
        if 'order_by' in self.request.GET:
            order_by = self.request.GET.get('order_by')
            
            reverse = False
            if order_by[0] == '-':
                order_by = order_by.replace('-', '')
                reverse = True
                
            if order_by in self.options:        
                if reverse:
                    for index, option in enumerate(self.options[order_by]):
                        self.options[order_by][index] = f"-{option}"
            return order_by
        else:
            return None
            
    def get_options(self):
        orderby_options = {'name' : [f'{self.name}_session__{self.name}', 'pk'], 
                        'execution_id': [f'{self.name}_session__execution_id'],
                        'timestamp': [f'{self.name}_session__create_timestamp'],
                        'execution_time': ['actual_execution_time'],
                        'application': [f'{self.application_order}__application__name'],
                        'job': [f'{self.job_order}__job__name'],
                        'connection_type': ['dataset_session__dataset__connection__connection_type'],
                        'comparison_results' : ['dataset_session__degree_of_change'],
                        'status_type': ['status_type']}
        return orderby_options

