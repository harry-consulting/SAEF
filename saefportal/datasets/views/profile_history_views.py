from bootstrap_modal_forms.generic import BSModalReadView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator

from datasets.models import Dataset
from users.mixins import ObjectPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class ReadProfileHistory(ObjectPermissionRequiredMixin, BSModalReadView):
    model = Dataset
    template_name = "datasets/dataset_detail/read_profile_history.html"
    object_permission = "view_dataset"

    def get_context_data(self, **kwargs):
        context = super(ReadProfileHistory, self).get_context_data()
        profile_runs = context["dataset"].get_profile_runs()

        if profile_runs:
            context["selected_run"] = profile_runs[0]

        return context


@login_required
def update_read_profile_history(request):
    selected_run = None
    dataset_id = request.GET.get("dataset_id", None)
    run_id = request.GET.get("run_id", None)

    dataset = Dataset.objects.get(id=dataset_id)

    # Only return information on the selected run if the requesting user has at least view permission for the dataset.
    if request.user.has_permission("view_dataset", dataset):
        selected_run = dataset.get_profile_runs().get(id=run_id)

    return render(request, "datasets/dataset_detail/read_profile_history.html",
                  {"dataset": dataset, "selected_run": selected_run})
