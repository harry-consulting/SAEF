from bootstrap_modal_forms.generic import BSModalFormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, DeleteView

from datalakes.forms import (GoogleCloudStorageDatalakeForm, FileStoreDatalakeForm, AzureDatalakeForm,
                             AmazonS3DatalakeForm)
from settings.forms import SettingsModelForm, UserProfileModelForm, DatalakeConnectionModelForm
from settings.models import Settings, Contact
from settings.util import modify_refresh_all_task, modify_delete_outdated_task, connect_to_datalake, \
    group_datalake_types
from users.mixins import AdminPermissionRequiredMixin
from users.models import UserProfile, User


@method_decorator(login_required, name="dispatch")
class SettingsUpdateView(SuccessMessageMixin, UpdateView):
    model = Settings
    template_name = "settings/settings.html"
    form_class = SettingsModelForm
    success_url = reverse_lazy("settings:settings", kwargs={"pk": 1})
    success_message = "Settings were updated."

    def get_context_data(self, **kwargs):
        context = super(SettingsUpdateView, self).get_context_data(**kwargs)

        initial_user_profile_data = model_to_dict(UserProfile.objects.get(user=self.request.user))
        initial_user_profile_data["email"] = User.objects.get(pk=self.request.user.pk).email
        context["user_profile_form"] = UserProfileModelForm(initial_user_profile_data)
        context["contacts"] = Contact.objects.all().order_by("name")

        context["datalake_type"] = str(self.object.datalake_type)

        return context

    def form_valid(self, form):
        # Saving the fields specified in the settings form.
        self.object = form.save()

        # Saving the fields specified in the user profile form.
        user_profile_data = {k: self.request.POST[k] for k in ["first_name", "last_name", "phone"]}
        UserProfile.objects.filter(user=self.request.user).update(**user_profile_data)

        User.objects.filter(pk=self.request.user.pk).update(email=self.request.POST["email"])

        modify_refresh_all_task(self.object, self.request)
        modify_delete_outdated_task(self.object, self.request)

        self.object.save()
        messages.success(self.request, self.success_message)

        return HttpResponseRedirect(self.get_success_url())


class DatalakeConnectionCreateUpdateView(AdminPermissionRequiredMixin, BSModalFormView):
    """Base class to avoid duplicated code between create and update view."""
    form_class = DatalakeConnectionModelForm
    success_url = reverse_lazy("settings:settings", args=[1])

    def get_context_data(self, **kwargs):
        context = super(DatalakeConnectionCreateUpdateView, self).get_context_data(**kwargs)
        context["grouped_datalake_types"] = group_datalake_types()

        return context

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            return connect_to_datalake(self.request, form)

        return HttpResponseRedirect(self.success_url)


@method_decorator(login_required, name="dispatch")
class DatalakeConnectionCreateView(DatalakeConnectionCreateUpdateView):
    template_name = "settings/datalake/create_datalake_connection.html"


@method_decorator(login_required, name="dispatch")
class DatalakeConnectionUpdateView(DatalakeConnectionCreateUpdateView):
    template_name = "settings/datalake/update_datalake_connection.html"


@method_decorator(login_required, name="dispatch")
class DatalakeConnectionDeleteView(AdminPermissionRequiredMixin, DeleteView):
    success_message = "Datalake connection was deleted."

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        Settings.objects.get().datalake.delete()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(reverse_lazy("settings:settings", args=[1]))


@login_required
def add_contact(request):
    name = request.POST.get("name", None)
    email = request.POST.get("email", None)

    Contact.objects.create(name=name, email=email)

    return render(request, "settings/contacts.html", {"contacts": Contact.objects.all().order_by("name")})


@login_required
@csrf_exempt
def delete_contact(request, contact_id):
    Contact.objects.filter(id=contact_id).delete()

    return render(request, "settings/contacts.html", {"contacts": Contact.objects.all().order_by("name")})


@login_required
def update_datalake_form(request):
    """Return rendered html with a form corresponding to the requested datalake."""
    datalake_type = request.GET.get("datalake_type", None)

    if datalake_type == "GOOGLE_CLOUD_STORAGE":
        form = GoogleCloudStorageDatalakeForm()
    elif datalake_type == "AZURE_BLOB_STORAGE" or datalake_type == "AZURE_DATA_LAKE":
        form = AzureDatalakeForm()
    elif datalake_type == "AMAZON_S3":
        form = AmazonS3DatalakeForm()
    else:
        form = FileStoreDatalakeForm()

    return render(request, "settings/datalake/datalake_form.html", {"datalake_form": form})
