import json

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalReadView, BSModalFormView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django_celery_beat.models import PeriodicTask

from analyzer.tasks import run_job_task
from jobs.forms.forms import JobModelForm
from jobs.models import Job
from jobs.util import clear_alert_fields, modify_periodic_tasks, get_task_form
from users.mixins import ObjectPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class JobListView(ListView):
    model = Job
    template_name = "jobs/index.html"
    context_object_name = "jobs"


@method_decorator(login_required, name="dispatch")
class JobDeleteView(ObjectPermissionRequiredMixin, DeleteView):
    model = Job
    success_url = reverse_lazy("jobs:index")
    success_message = "Job was deleted."
    object_permission = "delete_job"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Delete any potential periodic task connected to the job.
        PeriodicTask.objects.filter(name=self.get_object().id).delete()

        messages.success(self.request, self.success_message)
        return super(JobDeleteView, self).delete(request, *args, **kwargs)


class JobCreateUpdateView:
    """Parent class to avoid duplicated code between create and update view."""
    form_class = JobModelForm
    success_url = reverse_lazy("jobs:index")

    def form_valid(self, form):
        self.object = form.save()

        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            clear_alert_fields(self.object, self.request)
            self.object.save_without_historical_record()

            # If the job was previously scheduled or is now scheduled, modify the periodic tasks.
            if PeriodicTask.objects.filter(name=self.object.id).exists() or "schedule-checkbox" in self.request.POST:
                modify_periodic_tasks(self.object, self.request)

            messages.success(self.request, self.success_message)

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name="dispatch")
class JobCreateView(JobCreateUpdateView, BSModalCreateView):
    template_name = "jobs/create_update_job/create_job.html"
    success_message = "Job was created."


@method_decorator(login_required, name="dispatch")
class JobUpdateView(ObjectPermissionRequiredMixin, JobCreateUpdateView, BSModalUpdateView):
    model = Job
    template_name = "jobs/create_update_job/update_job.html"
    success_message = "Job was updated."
    object_permission = "update_job"


@method_decorator(login_required, name="dispatch")
class RunHistoryReadView(ObjectPermissionRequiredMixin, BSModalReadView):
    model = Job
    template_name = "jobs/read_run_history.html"
    object_permission = "view_job"


@method_decorator(login_required, name="dispatch")
class TriggerJobView(ObjectPermissionRequiredMixin, BSModalFormView):
    template_name = "jobs/trigger_job.html"
    success_message = "Success: Job was started."
    success_url = reverse_lazy("jobs:index")
    model = Job
    object_permission = "execute_job"

    def dispatch(self, request, *args, **kwargs):
        self.job = Job.objects.get(pk=self.kwargs["pk"])
        return super(TriggerJobView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_task_form(self.job.get_task()[1])

    def get_initial(self):
        """Set the initial parameters to the last used parameters, if empty try to set it to the schedule parameters."""
        last_job_run = self.job.get_last_job_run()
        periodic_task = self.job.get_periodic_task()

        if periodic_task:
            return json.loads(periodic_task.kwargs)["task_parameters"]
        elif last_job_run:
            return last_job_run.parameters
        else:
            return {}

    def form_valid(self, form):
        # Bootstrap modal forms POSTs twice, one ajax POST for form validation and another for saving.
        if not self.request.is_ajax():
            run_job_task.delay(self.job.id, self.request.user.email, form.cleaned_data)

        return HttpResponseRedirect(self.get_success_url())


@login_required
def update_task_form(request):
    form_data = {}
    job_id = request.GET.get("job_id", None)

    # If given a job id, the request is from the "update job" modal. If so, initialize the form with the existing data.
    if job_id:
        job = Job.objects.get(pk=job_id)

        # Only initialize the form data if the requesting user has at least view permission for the job.
        if request.user.has_permission("view_job", job):
            periodic_task = job.get_periodic_task()
            if periodic_task:
                form_data = json.loads(periodic_task.kwargs)["task_parameters"]

    task_name = request.GET.get("task_name", None)
    form = get_task_form(task_name)(initial=form_data)

    return render(request, "jobs/create_update_job/task_parameters.html", {"task_form": form})
