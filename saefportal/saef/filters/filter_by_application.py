from saef.models import Application


class FilterByApplication():
    '''
    Filter to show specific application in a session
    Requires GET request with 'status_option' argument
    and a application_session path e.g 'job_session__application_session'
    '''
    def __init__(self, request, application_session_path):
        self.request = request
        self.application_session_path = application_session_path
        self.options = self.get_options()
        self.selected = self.get_selected()
        
    def filter(self, sessions_metadata):
        status_filter = self.options[self.selected]
        sessions_metadata = sessions_metadata.filter(**status_filter)
            
        return sessions_metadata

    def get_selected(self):
        application_selected = 'All applications'
        
        if 'application_option' in self.request.GET  and self.request.GET.get('application_option') in self.options:
            application_selected = self.request.GET.get('application_option')
            
        return application_selected
            
    def get_options(self):
        application_options = {'All applications' : {}}
        
        applications = Application.objects.all() 
        for application in applications:
            application_options[application.name] = {f'{self.application_session_path}__application__name': application.name}
            
        return application_options