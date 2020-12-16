from django.contrib import messages

from saefportal.settings import MSG_SUCCESS_APPLICATION_SAVED, MSG_SUCCESS_APPLICATION_DELETED, \
    MSG_SUCCESS_APPLICATION_UPDATED
from ..models import Application
from ..forms import AddApplicationForm, UpdateApplicationForm

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

ADD_APPLICATION_TITLE = "Add Application"
UPDATE_APPLICATION_TITLE = 'Manage Application'
TEMPLATE_NAME = 'application/manage_application.html'


class ApplicationView(LoginRequiredMixin, generic.ListView):
    template_name = 'application/application_list.html'
    model = Application
    context_object_name = 'applications'


@login_required()
def update_application(request, application_id):
    if request.method == "POST":
        application_instance = Application.objects.get(pk=application_id)
        if request.POST["Operation"] == 'Delete':
            application_instance.delete()
            messages.success(request, MSG_SUCCESS_APPLICATION_DELETED)
            return redirect('application')
        else:
            form = UpdateApplicationForm(request.POST, instance=application_instance)
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, MSG_SUCCESS_APPLICATION_UPDATED)
                return redirect('application')

    if request.method == "GET":
        application = get_object_or_404(Application, id=application_id)
        form = UpdateApplicationForm(instance=application)
        context = {'form': form, 'title': UPDATE_APPLICATION_TITLE}
        return render(request, TEMPLATE_NAME, context)


@login_required()
def add_application(request):
    if request.method == "POST":
        form = AddApplicationForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            messages.success(request, MSG_SUCCESS_APPLICATION_SAVED)
            return redirect('application')
    else:
        form = AddApplicationForm()

    context = {'form': form, 'title': ADD_APPLICATION_TITLE}
    return render(request, TEMPLATE_NAME, context)
