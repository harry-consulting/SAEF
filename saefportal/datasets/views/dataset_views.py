import os

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, DeleteView
from pyspark.sql.utils import AnalysisException

from datalakes.util import save_upload_to_datalake
from datasets.forms import (QueryDatasetModelForm, ImportDatasetsModelForm, UpdateDatasetModelForm,
                            UploadDatasetsModelForm)
from datasets.models import Connection, Dataset
from datasets.util import data_overview, import_datasets, get_uploaded_datasets, remove_existing_datasets
from settings.mixins import DatalakeRequiredMixin
from users.mixins import ObjectPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class DatasetDetailView(ObjectPermissionRequiredMixin, DetailView):
    model = Dataset
    template_name = "datasets/dataset_detail/dataset_detail.html"
    object_permission = "view_dataset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["connections"] = Connection.objects.all().order_by("name")
        context["uploaded_datasets"] = get_uploaded_datasets()
        context["notes"] = self.object.get_notes()

        context["data_overview_datetime"], context["column_types"], context["data_preview"] = data_overview(self.object)

        return context


@method_decorator(login_required, name="dispatch")
class QueryDatasetCreateView(DatalakeRequiredMixin, BSModalCreateView):
    template_name = "datasets/dataset/create_query_dataset.html"
    form_class = QueryDatasetModelForm

    def get_success_message(self, cleaned_data):
        return "Success: Dataset was created." if self.object.id else None

    def get_success_url(self):
        return reverse_lazy("datasets:dataset_detail", kwargs={"pk": self.object.id}) if self.object.id else ""

    def get_form_kwargs(self):
        kwargs = super(QueryDatasetCreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs


@method_decorator(login_required, name="dispatch")
class ImportDatasetsCreateView(DatalakeRequiredMixin, BSModalCreateView):
    template_name = "datasets/dataset/import_datasets.html"
    form_class = ImportDatasetsModelForm
    success_message = "Datasets were imported."
    success_url = reverse_lazy("datasets:index")

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            # Ensure the user has the correct permissions to avoid malicious users manipulating the UI to access
            # connections they are not authorized to use.
            if self.request.user.has_permission("update_connection", form.cleaned_data["connection"]):
                import_datasets(self.request.POST.getlist("dataset-select"), form)
                messages.success(self.request, self.success_message)

        return HttpResponseRedirect(reverse_lazy("datasets:index"))

    def get_form_kwargs(self):
        kwargs = super(ImportDatasetsCreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs


@method_decorator(login_required, name="dispatch")
class UploadDatasetsCreateView(DatalakeRequiredMixin, BSModalCreateView):
    template_name = "datasets/dataset/upload_datasets.html"
    form_class = UploadDatasetsModelForm
    success_url = reverse_lazy("datasets:index")

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            successful_uploads = []
            failed_uploads = []
            files = self.request.FILES.getlist("files")

            # For each uploaded file, create a dataset and save the content of the file to the datalake.
            for file in files:
                name = os.path.splitext(file.name)[0]

                # Only create a dataset if a file with the same name has not been uploaded already.
                if not Dataset.objects.filter(name=name, connection__isnull=True).exists():
                    dataset = Dataset.objects.create(name=name, owner=form.cleaned_data["owner"],
                                                     tags=form.cleaned_data["tags"], type=Dataset.Type.TABLE)
                    dataset.contacts.add(*form.cleaned_data["contacts"])

                    save_upload_to_datalake(file)
                    successful_uploads.append(file.name)
                else:
                    failed_uploads.append(file.name)

            if len(successful_uploads) > 0:
                messages.success(self.request, f"Uploaded files: {', '.join(successful_uploads)}.")

            if len(failed_uploads) > 0:
                messages.error(self.request, f"Failed to upload files: {', '.join(failed_uploads)}.")

        return HttpResponseRedirect(reverse_lazy("datasets:index"))


@method_decorator(login_required, name="dispatch")
class DatasetUpdateView(ObjectPermissionRequiredMixin, BSModalUpdateView):
    model = Dataset
    template_name = "datasets/dataset/update_dataset.html"
    form_class = UpdateDatasetModelForm
    success_message = "Success: Dataset was updated."
    object_permission = "update_dataset"

    def get_success_url(self):
        return reverse_lazy("datasets:dataset_detail", kwargs={"pk": self.object.id})


@method_decorator(login_required, name="dispatch")
class DatasetDeleteView(ObjectPermissionRequiredMixin, DeleteView):
    model = Dataset
    success_url = reverse_lazy("datasets:index")
    success_message = "Dataset was deleted."
    object_permission = "delete_dataset"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DatasetDeleteView, self).delete(request, *args, **kwargs)


@login_required
def query_preview(request):
    """Apply the query to the connection and return render with the column names and a preview of the data."""
    connection_id = request.POST.get("connection_id", None)
    query = request.POST.get("query", None)

    connection = Connection.objects.get(id=connection_id)

    # Only get the data preview if the requesting user has at least view permission for the connection.
    if request.user.has_permission("view_connection", connection):
        try:
            data_df = connection.datastore.retrieve_data(query=query, limit=10)

            column_names = list(data_df)
            data_preview = list(data_df.itertuples(index=False, name=None))

            context = {"query_valid": True, "column_names": column_names, "data_preview": data_preview}
        except (TypeError, ValueError, AnalysisException):
            context = {"query_valid": False}
    else:
        context = {"query_valid": False}

    return render(request, "datasets/dataset/query_result.html", context)


@login_required
def connection_datasets(request):
    """Return render with all possible datasets for the given connection (either tables or views)."""
    connection_id = request.GET.get("connection_id", None)
    select_multiple = request.GET.get("select_multiple", None)

    connection = Connection.objects.get(id=connection_id)

    # Ensure the user has the correct permissions to avoid malicious users manipulating the UI to access
    # connections they are not authorized to use.
    if request.user.has_permission("update_connection", connection):
        viable_datasets = connection.datastore.get_viable_datasets()

        # If select_multiple is True, the request is from the "Import datasets" modal, so we remove existing datasets.
        if select_multiple == "True":
            viable_datasets = remove_existing_datasets(viable_datasets, connection)
    else:
        viable_datasets = []

    context = {"connection_datasets": viable_datasets, "select_multiple": select_multiple}
    return render(request, "datasets/dataset/dataset_select.html", context)
