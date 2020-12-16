
PREDEFINED_COLUMNS = ['csrfmiddlewaretoken', 'selected']

class FilterByColumn():
    def __init__(self, request):
        self.request = request
        self.selected_columns = self.get_selected()
        
    def get_selected(self):
        selected_columns = {}
        
        for column in self.request.POST:
            if column in PREDEFINED_COLUMNS:
                continue
            selected_columns[column] = self.request.POST.get(column)
            
        selected = self.request.POST.get('selected')
        if selected:
            if selected_columns[selected] == 'true':
                selected_columns[selected] = 'false'
            elif selected_columns[selected] == 'false':
                selected_columns[selected] = 'true'
                
        return selected_columns