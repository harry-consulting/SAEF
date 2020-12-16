from django.contrib import messages

from saefportal.settings import MSG_SUCCESS_JOB_SAVED, MSG_SUCCESS_JOB_DELETED, MSG_SUCCESS_JOB_UPDATED
from ..models import Job
from ..forms import AddJobForm, UpdateJobForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

ADD_JOB_TITLE = 'Add Job'
UPDATE_JOB_TITLE = 'Manage Job'
TEMPLATE_NAME = 'job/manage_job.html'


class JobView(LoginRequiredMixin, generic.ListView):
    template_name = 'job/job_list.html'
    model = Job
    context_object_name = 'jobs'


@login_required()
def update_job(request, job_id):
    if request.method == "POST":
        instance = Job.objects.get(pk=job_id)
        if request.POST["Operation"] == 'Delete':
            instance.delete()
            messages.success(request, MSG_SUCCESS_JOB_DELETED)
            return redirect('job')
        else:
            form = UpdateJobForm(request.POST, instance=instance)
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, MSG_SUCCESS_JOB_UPDATED)
                context = {'form': form, 'title': UPDATE_JOB_TITLE}
                return render(request, TEMPLATE_NAME, context)

    if request.method == "GET":
        job = get_object_or_404(Job, id=job_id)
        form = UpdateJobForm(instance=job)
        context = {'form': form, 'title': UPDATE_JOB_TITLE}
        return render(request, TEMPLATE_NAME, context)


@login_required()
def add_job(request):
    if request.method == "POST":
        form = AddJobForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            messages.success(request, MSG_SUCCESS_JOB_SAVED)
            return redirect('job')
    else:
        form = AddJobForm()

    context = {'form': form, 'title': ADD_JOB_TITLE}
    return render(request, TEMPLATE_NAME, context)
