from ..models import Dataset

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic


class ManageView(LoginRequiredMixin, generic.ListView):
    template_name = 'main/manage.html'
    model = Dataset
    context_object_name = 'latest_dataset_list'
