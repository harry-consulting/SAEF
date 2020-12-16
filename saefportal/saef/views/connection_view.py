from saef.connections import ConnectionFormHelper
from ..models import Connection
from ..forms import ConnectionTypeForm

from saefportal.settings import MSG_SUCCESS_CONNECTION_UPDATE, MSG_SUCCESS_CONNECTION_VALID, \
    MSG_ERROR_CONNECTION_INVALID, MSG_SUCCESS_CONNECTION_SAVED, MSG_ERROR_CONNECTION_SELECT_INVALID, \
    MSG_SUCCESS_CONNECTION_DELETED

from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

ADD_CONNECTION_TITLE = 'Add Connection'

ADD_CONNECTION_TEMPLATE_NAME = "connection/add_connection.html"
EDIT_CONNECTION_TEMPLATE_NAME = "connection/edit_connection_detail.html"
POSTGRESQL_NAME = "PostgreSQL"


class ConnectionView(LoginRequiredMixin, generic.ListView):
    template_name = 'connection/connection_list.html'
    model = Connection
    context_object_name = 'connections'


@login_required()
def update_connection(request, connection_id):
    helper = ConnectionFormHelper()
    connection = get_object_or_404(Connection, id=connection_id)

    if request.method == "POST":
        if request.POST["Operation"] == 'Delete':
            instance = Connection.objects.get(pk=connection_id)
            instance.delete()
            messages.success(request, MSG_SUCCESS_CONNECTION_DELETED)
            return redirect('connection')
        else:
            edit_method = helper.lookup_connection(connection.connection_type.name, 'edit')
            edit_form = edit_method(post_request=request.POST)
            if edit_form.is_valid():
                save_edit_method = helper.lookup_connection(connection.connection_type.name, 'save_edit')
                save_edit_method(edit_form, connection_id)
                messages.success(request, MSG_SUCCESS_CONNECTION_UPDATE)
                return redirect("connection")
            else:
                messages.error(request, MSG_ERROR_CONNECTION_SELECT_INVALID)
                context = {"connection_form": edit_form}
                return render(request, EDIT_CONNECTION_TEMPLATE_NAME, context)

    edit_method = helper.lookup_connection(connection.connection_type.name, 'edit')
    edit_form = edit_method(connection_pk=connection.pk)
    context = {"connection_form": edit_form}
    return render(request, EDIT_CONNECTION_TEMPLATE_NAME, context)


@login_required()
def test_database_connection(request, form):
    helper = ConnectionFormHelper()
    connection_type = form.cleaned_data['connection_type'].name

    add_form_method = helper.lookup_connection(connection_type, 'add')
    connection_form = add_form_method(request.POST)
    if connection_form.is_valid():
        test_connection_method = helper.lookup_connection(connection_type, 'test')
        result = test_connection_method(connection_form.cleaned_data, form.cleaned_data)
        if result is True:
            messages.success(request, MSG_SUCCESS_CONNECTION_VALID)
        else:
            messages.error(request, MSG_ERROR_CONNECTION_INVALID(result))

    context = {
        'form': form,
        'connection_form': add_form_method(request.POST),
        'connection_type': connection_type
    }
    return render(request, ADD_CONNECTION_TEMPLATE_NAME, context)


@login_required()
def save_connection(request, form):
    helper = ConnectionFormHelper()
    connection_type = form.cleaned_data['connection_type'].name

    add_form_method = helper.lookup_connection(connection_type, 'add')
    connection_form = add_form_method(request.POST)
    if connection_form.is_valid():
        save_method = helper.lookup_connection(connection_type, 'save')
        save_method(connection_form.cleaned_data, form.cleaned_data)
        messages.success(request, MSG_SUCCESS_CONNECTION_SAVED)
        return redirect("connection")

    messages.error(request, MSG_ERROR_CONNECTION_SELECT_INVALID)
    connection_type = form.cleaned_data['connection_type'].name

    context = {
        "form": ConnectionTypeForm(request.POST),
        "connection_form": add_form_method(request.POST),
        "connection_type": connection_type
    }
    return render(request, ADD_CONNECTION_TEMPLATE_NAME, context)


@login_required()
def add_connection(request):
    helper = ConnectionFormHelper()

    if request.method == "POST":
        form = ConnectionTypeForm(request.POST)
        if form.is_valid() and form.cleaned_data['connection_type']:
            connection_type = form.cleaned_data['connection_type'].name
            if "Operation" not in request.POST:
                add_form_method = helper.lookup_connection(connection_type, 'add')
                context = {
                    "form": form,
                    "connection_form": add_form_method(),
                    "connection_type": connection_type
                }
                return render(request, ADD_CONNECTION_TEMPLATE_NAME, context)
            elif request.POST["Operation"] == "Test":
                return test_database_connection(request, form)
            elif request.POST["Operation"] == "Save":
                return save_connection(request, form)
    else:
        form = ConnectionTypeForm()
    return render(request, ADD_CONNECTION_TEMPLATE_NAME, {'form': form})
