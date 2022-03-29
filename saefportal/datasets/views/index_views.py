from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from datasets.models import Connection, Dataset
from datasets.util import get_uploaded_datasets


@login_required
def index(request):
    context = {"connections": Connection.objects.all().order_by("name"), "uploaded_datasets": get_uploaded_datasets()}

    return render(request, "datasets/index.html", context)


@method_decorator(login_required, name="dispatch")
class SearchDatasetsListView(ListView):
    model = Dataset
    template_name = "datasets/search_datasets.html"
    paginate_by = 5
    context_object_name = "search_datasets"
    ordering = ["name"]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context["connections"] = Connection.objects.all()
        context["datasets"] = Dataset.objects.all()

        return context

    def get_queryset(self):
        search_term = self.request.GET.get("q", "")

        return Dataset.objects.filter(name__icontains=search_term) | Dataset.objects.filter(tags__icontains=search_term)
