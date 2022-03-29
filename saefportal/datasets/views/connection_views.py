from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView

import datastores.forms
from datasets.forms import CreateConnectionModelForm, UpdateConnectionModelForm
from datasets.models import Connection
from datasets.util import create_database_datastore, group_connection_types, connect_to_datastore
from settings.mixins import DatalakeRequiredMixin
from users.mixins import ObjectPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class ConnectionCreateView(DatalakeRequiredMixin, BSModalCreateView):
    form_class = CreateConnectionModelForm
    template_name = "datasets/connection/create_connection.html"
    success_url = reverse_lazy("datasets:index")

    def get_context_data(self, **kwargs):
        context = super(ConnectionCreateView, self).get_context_data(**kwargs)
        context["grouped_connection_types"] = group_connection_types()

        return context

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            return connect_to_datastore(self.request, form)

        return HttpResponseRedirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class ConnectionUpdateView(ObjectPermissionRequiredMixin, BSModalUpdateView):
    model = Connection
    form_class = UpdateConnectionModelForm
    success_url = reverse_lazy("datasets:index")
    template_name = "datasets/connection/update_connection.html"
    success_message = "Success: Connection was updated."
    object_permission = "update_connection"


@method_decorator(login_required, name="dispatch")
class ConnectionDeleteView(ObjectPermissionRequiredMixin, DeleteView):
    model = Connection
    success_url = reverse_lazy("datasets:index")
    success_message = "Connection was deleted."
    object_permission = "delete_connection"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        datastore = self.get_object().datastore
        if datastore:
            datastore.delete()

        messages.success(self.request, self.success_message)

        return super(ConnectionDeleteView, self).delete(request, *args, **kwargs)


@login_required
def test_connection(request):
    """Validate that the given connection works using a temporary datastore."""
    datastore = create_database_datastore(request.POST)

    return JsonResponse({"connection_valid": datastore.is_connection_valid()})


@login_required
def update_datastore_form(request):
    """Return rendered html with a form corresponding to the requested datastore."""
    datastore_type = request.GET.get("datastore_type", None)

    if datastore_type == Connection.Type.POSTGRES:
        form = datastores.forms.PostgresDatastoreModelForm()
    elif datastore_type == Connection.Type.AZURE:
        form = datastores.forms.AzureDatastoreModelForm()
    elif datastore_type == Connection.Type.GOOGLE_CLOUD_STORAGE:
        form = datastores.forms.GoogleCloudStorageDatastoreForm()
    elif datastore_type == Connection.Type.AZURE_BLOB_STORAGE or datastore_type == Connection.Type.AZURE_DATA_LAKE:
        form = datastores.forms.AzureDatastoreForm()
    elif datastore_type == Connection.Type.AMAZON_S3:
        form = datastores.forms.AmazonS3DatastoreForm()
    else:
        form = datastores.forms.FileDatastoreForm()

    return render(request, "datasets/connection/datastore_form.html", {"form": form})
