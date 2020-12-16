from django.contrib import messages

from saefportal.settings import MSG_SUCCESS_APPLICATION_TOKEN_SAVED, MSG_SUCCESS_APPLICATION_TOKEN_UPDATED, \
    MSG_SUCCESS_APPLICATION_TOKEN_DELETED
from ..models import ApplicationToken
from ..forms import AddApplicationTokenForm, UpdateApplicationTokenForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

ADD_APPLICATION_TOKEN_TILE = "Add Application Token"
EDIT_APPLICATION_TOKEN_TITLE = "Manage Application Token"
MANAGE_APPLICATION_TOKEN_TEMPLATE_NAME = "application_token/manage_application_token.html"


class ApplicationTokenView(LoginRequiredMixin, generic.ListView):
    template_name = 'application_token/application_token_list.html'
    model = ApplicationToken
    context_object_name = 'application_tokens'


@login_required()
def update_application_token(request, application_token_id):
    if request.method == "POST":
        instance = ApplicationToken.objects.get(pk=application_token_id)
        if request.POST["Operation"] == 'Delete':
            instance.delete()
            messages.success(request, MSG_SUCCESS_APPLICATION_TOKEN_DELETED)
            return redirect('application_token')
        else:
            form = UpdateApplicationTokenForm(request.POST, instance=instance)
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                messages.success(request, MSG_SUCCESS_APPLICATION_TOKEN_UPDATED)
                context = {'form': form, 'title': EDIT_APPLICATION_TOKEN_TITLE}
                return render(request, MANAGE_APPLICATION_TOKEN_TEMPLATE_NAME, context)

    if request.method == "GET":
        instance = get_object_or_404(ApplicationToken, id=application_token_id)
        form = UpdateApplicationTokenForm(instance=instance)
        context = {'form': form, 'title': EDIT_APPLICATION_TOKEN_TITLE}
        return render(request, MANAGE_APPLICATION_TOKEN_TEMPLATE_NAME, context)


@login_required()
def add_application_token(request):
    if request.method == "POST":
        form = AddApplicationTokenForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            messages.success(request, MSG_SUCCESS_APPLICATION_TOKEN_SAVED)
            return redirect("application_token")
    else:
        form = AddApplicationTokenForm()

    context = {'form': form, 'title': ADD_APPLICATION_TOKEN_TILE}
    return render(request, MANAGE_APPLICATION_TOKEN_TEMPLATE_NAME, context)
