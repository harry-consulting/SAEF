
class FilterByStatus():
    '''
    Filter to show specific status in a session
    Requires GET request with 'status_option' argument 
    and the name of the session object, e.g application, job, dataset
    '''
    def __init__(self, request):
        self.request = request
        self.options = self.get_options()
        self.selected = self.get_selected()
        
    def filter(self, sessions_metadata):
        status_filter = self.options[self.selected]
        sessions_metadata = sessions_metadata.filter(**status_filter)
            
        return sessions_metadata

    def get_selected(self):
        status_selected = 'All status'
        
        if 'status_option' in self.request.GET  and self.request.GET.get('status_option') in self.options:
            status_selected = self.request.GET.get('status_option')
            
        return status_selected
            
    def get_options(self):
        status_options = {'All status' : {}, 
                        'Succeeded': {'status_type': 'SUCCEEDED'},
                        'Succeeded with issue': {'status_type': 'SUCCEEDED_ISSUE'},
                        'Failed': {'status_type': 'FAILED'}}
        return status_options