from saef.models import Job


class FilterByJob():
    '''
    Filter to show specific job in a session
    Requires GET request with 'status_option' argument
    and application_name to filter the jobs that belong to the application
    '''
    def __init__(self, request, application_name='All applications'):
        self.request = request
        self.application_name = application_name
        self.options = self.get_options()
        self.selected = self.get_selected()
        
    def filter(self, sessions_metadata):
        status_filter = self.options[self.selected]
        sessions_metadata = sessions_metadata.filter(**status_filter)
            
        return sessions_metadata

    def get_selected(self):
        job_selected = 'All jobs'
        
        if 'job_option' in self.request.GET  and self.request.GET.get('job_option') in self.options:
            job_selected = self.request.GET.get('job_option')
            
        return job_selected
            
    def get_options(self):
        job_options = {'All jobs' : {}}
        
        if self.application_name == 'All applications':
            jobs = Job.objects.all() 
        else:
            jobs = Job.objects.filter(application__name=self.application_name) 
            
        for job in jobs:
            job_options[job.name] = {'dataset_session__job_session__job__name': job.name}
            
        return job_options