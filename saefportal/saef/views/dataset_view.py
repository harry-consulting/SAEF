import psycopg2
from azure.core.exceptions import ResourceNotFoundError
from django.core.exceptions import ObjectDoesNotExist

from saef.enums import ConnectionType, DatasetAccess
from pyspark.sql.utils import AnalysisException, ParseException
from ..models import Dataset, Connection, AzureBlobStorageConnection
from ..forms import AddDatasetForm, EditDatasetForm, SelectConnectionForm, DatasetWithoutSQLForm, \
    DatasetWithoutTableForm, AddAzureBlobStorageDatasetForm, EditAzureBlobStorageDatasetForm

from saefportal.settings import MSG_ERROR_NO_DATABASE_CONNECTION, MSG_SUCCESS_DATASET_SAVED, \
    MSG_SUCCESS_DATASET_CREATE, MSG_ERROR_DATASET_FORM_INVALID

from analyzer.recordset.recordset_factory import recordset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

SELECT_DATASET_CONNECTION_TEMPLATE_NAME = 'dataset/select_connection.html'
ADD_DATASET_TEMPLATE_NAME = 'dataset/dataset_add.html'
EDIT_DATASET_TEMPLATE_NAME = 'dataset/dataset_detail.html'
PREVIEW_DATASET_TEMPLATE_NAME = 'dataset/dataset_preview.html'


class DatasetView(LoginRequiredMixin, generic.ListView):
    template_name = 'dataset/dataset_list.html'
    model = Dataset
    context_object_name = 'datasets'


class DetailDatasetView(LoginRequiredMixin, generic.DetailView):
    model = Dataset
    template_name = 'dataset/detail_dataset.html'


def get_connection(connection_id):
    try:
        return Connection.objects.get(pk=connection_id)
    except ObjectDoesNotExist:
        return None


def get_all_tables(dataset):
    db = recordset_factory(dataset)
    results = db.get_all_tables()
    if type(results) is psycopg2.OperationalError:
        return None
    table_list = []
    for table in results:
        name = f'{table[0]}.{table[1]}'
        table_list.append((name, name))

    return table_list


def get_edit_dataset_form(data, dataset_instance):
    table_list = get_all_tables(dataset_instance)
    return EditDatasetForm(table_list, data=data, instance=dataset_instance)


def get_add_dataset_form(post_data):
    connection = Connection.objects.get(pk=post_data["connection"])
    dataset = Dataset(
        connection=connection,
        dataset_access_method=post_data["dataset_access_method"],
        dataset_extraction_table=post_data["dataset_extraction_table"],
        dataset_extraction_sql=post_data["dataset_extraction_sql"]
    )
    table_list = get_all_tables(dataset)
    return AddDatasetForm(table_list, data=post_data)


def find_appropriate_dataset_form(add_dataset_form, post_data, **kwargs):
    if dataset_form_uses_table(add_dataset_form):
        return DatasetWithoutSQLForm(post_data, **kwargs)
    elif dataset_form_uses_sql(add_dataset_form):
        return DatasetWithoutTableForm(post_data, **kwargs)
    else:
        return None


def dataset_form_uses_table(dataset_form):
    return "dataset_extraction_sql" in dataset_form.errors and "dataset_extraction_table" in dataset_form.cleaned_data


def dataset_form_uses_sql(dataset_form):
    return "dataset_extraction_sql" in dataset_form.cleaned_data


def save_dataset(dataset_form):
    if dataset_form is None:
        return False
    elif dataset_form.is_valid():
        data = dataset_form.save(commit=False)
        data.save()
        return True
    else:
        return False


def save_azure_blob_storage_data(dataset_form):
    if dataset_form is None:
        return False
    elif dataset_form.is_valid():
        dataset = Dataset(
            sequence_in_job=dataset_form.cleaned_data["sequence_in_job"],
            dataset_name=dataset_form.cleaned_data["dataset_name"],
            dataset_type=dataset_form.cleaned_data["dataset_type"],
            query_timeout=dataset_form.cleaned_data["query_timeout"],
            dataset_access_method=DatasetAccess.SQL.value,
            dataset_extraction_sql=dataset_form.cleaned_data["dataset_extraction_sql"],
            connection=dataset_form.cleaned_data["connection"],
            job=dataset_form.cleaned_data["job"]
        )
        dataset.save()
        return True
    else:
        return False


def save_edit_azure_blob_storage_data(dataset_form):
    if dataset_form is None:
        return False
    elif dataset_form.is_valid():
        dataset = dataset_form.instance

        dataset.sequence_in_job = dataset_form.cleaned_data["sequence_in_job"]
        dataset.dataset_name = dataset_form.cleaned_data["dataset_name"]
        dataset.dataset_type = dataset_form.cleaned_data["dataset_type"]
        dataset.query_timeout = dataset_form.cleaned_data["query_timeout"]
        dataset.dataset_access_method = DatasetAccess.SQL.value
        dataset.dataset_extraction_sql = dataset_form.cleaned_data["dataset_extraction_sql"]
        dataset.connection = dataset_form.cleaned_data["connection"]
        dataset.job = dataset_form.cleaned_data["job"]

        dataset.save()
        return True
    else:
        return False


@login_required()
def update_dataset(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)

    if request.method == "POST":
        if "Operation" not in request.POST:
            dataset.connection = get_connection(request.POST["connection"])
            if dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
                initial = {key: value[0] for key, value in dict(request.POST).items()}
                edit_form = EditAzureBlobStorageDatasetForm(initial=initial)
                context = {"edit_form": edit_form}
                return render(request, EDIT_DATASET_TEMPLATE_NAME, context)
            else:
                table_list = get_all_tables(dataset)
                if table_list is not None:
                    enable_manage = True if dataset.dataset_access_method == "TABLE" else False
                    initial = {key: value[0] for key, value in dict(request.POST).items()}
                    edit_dataset_form = EditDatasetForm(table_list, enable_manage, initial=initial)
                    context = {"edit_form": edit_dataset_form}
                    return render(request, EDIT_DATASET_TEMPLATE_NAME, context)
                else:
                    messages.error(request, MSG_ERROR_NO_DATABASE_CONNECTION(dataset.connection))
                    initial = {key: value[0] for key, value in dict(request.POST).items()}
                    initial["connection"] = 0
                    edit_form = EditDatasetForm([], False, initial=initial)
                    context = {"edit_form": edit_form}
                    return render(request, EDIT_DATASET_TEMPLATE_NAME, context)
        elif request.POST["Operation"] == 'Delete':
            dataset.delete()
            return redirect('saef_dataset')
        elif request.POST["Operation"] == 'Save':
            if dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
                edit_dataset_form = EditAzureBlobStorageDatasetForm(data=request.POST, instance=dataset)
                saved = save_edit_azure_blob_storage_data(edit_dataset_form)
            else:
                edit_dataset_form = get_edit_dataset_form(request.POST, dataset)
                dataset_form = find_appropriate_dataset_form(edit_dataset_form, request.POST, instance=dataset)
                saved = save_dataset(dataset_form)
            if saved:
                messages.success(request, MSG_SUCCESS_DATASET_SAVED)
                return redirect("saef_dataset")
            else:
                messages.error(request, MSG_ERROR_DATASET_FORM_INVALID)
                context = {"edit_form": edit_dataset_form}
                return render(request, EDIT_DATASET_TEMPLATE_NAME, context)
        elif request.POST["Operation"] == 'Manage Column':
            return redirect('manage_column', dataset_id=dataset_id)
        elif request.POST["Operation"] == 'Manage Constraint':
            return redirect('manage_constraint', dataset_id=dataset_id)
        elif request.POST["Operation"] == 'Preview':
            return preview_dataset(request, dataset)

    if dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
        edit_form = EditAzureBlobStorageDatasetForm(instance=dataset)
        context = {"edit_form": edit_form}
        return render(request, EDIT_DATASET_TEMPLATE_NAME, context)
    else:
        all_table_list = get_all_tables(dataset)
        table_list = all_table_list if all_table_list is not None else []
        enable_managed = True if dataset.dataset_access_method == 'TABLE' else False
        edit_form = EditDatasetForm(table_list, enable_managed, instance=dataset)
        context = {'edit_form': edit_form}
        return render(request, EDIT_DATASET_TEMPLATE_NAME, context)


def query_does_not_contain_syntax_error(result):
    """If the psycopg2 exception has a pgcode of 42601, then there exists a syntax error in the SQL statement"""
    return type(result) is not psycopg2.errors.lookup("42601")


def table_is_not_undefined(result):
    """If the psycopg2 exception has a pgcode of 42P01, then the table in the query is undefined"""
    return type(result) is not psycopg2.errors.lookup("42P01")


def there_is_not_a_database_error(result):
    return type(result) is not psycopg2.DatabaseError


def result_is_not_a_parse_exception(result):
    return type(result) is not ParseException


def result_is_not_a_analysis_exception(result):
    return type(result) is not AnalysisException


def render_error_template(request, e):
    messages.error(request, e)
    edit_form = EditAzureBlobStorageDatasetForm(request.POST)
    context = {'edit_form': edit_form}
    return render(request, EDIT_DATASET_TEMPLATE_NAME, context)


def preview_dataset(request, dataset):
    try:
        db = recordset_factory(dataset)
    except ResourceNotFoundError as e:
        return render_error_template(request, e)
    except ValueError as e:
        return render_error_template(request, e)

    result = db.extract_preview(request.POST['query_timeout'])

    if (there_is_not_a_database_error(result)
            and table_is_not_undefined(result)
            and query_does_not_contain_syntax_error(result)
            and result_is_not_a_parse_exception(result)
            and result_is_not_a_analysis_exception(result)):
        context = {'column_names': result[0], 'result': result[1:]}
        return render(request, PREVIEW_DATASET_TEMPLATE_NAME, context)
    else:
        if dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
            messages.error(request, result)
            edit_form = EditAzureBlobStorageDatasetForm(request.POST)
        else:
            messages.error(request, result.pgerror)
            edit_form = EditDatasetForm([], False, request.POST)
        context = {'edit_form': edit_form}
        return render(request, EDIT_DATASET_TEMPLATE_NAME, context)


@login_required()
def add_dataset(request):
    if request.method == "POST":
        select_connection_form = SelectConnectionForm(request.POST)
        if "Operation" not in request.POST:
            connection = Connection.objects.get(pk=request.POST["connection"])
            dataset = Dataset(
                connection=connection,
                dataset_access_method="TABLE",
                dataset_extraction_table="nonExistentSchema.nonExistentTable"
            )
            if connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
                add_dataset_form = AddAzureBlobStorageDatasetForm(initial={"connection": request.POST["connection"]})
                context = {"add_dataset_form": add_dataset_form}
                return render(request, ADD_DATASET_TEMPLATE_NAME, context)
            else:
                table_list = get_all_tables(dataset)
                if table_list is not None:
                    add_dataset_form = AddDatasetForm(table_list, initial={"connection": request.POST["connection"]})
                    context = {"add_dataset_form": add_dataset_form}
                    return render(request, ADD_DATASET_TEMPLATE_NAME, context)
                else:
                    messages.error(request, MSG_ERROR_NO_DATABASE_CONNECTION(connection))
                    context = {"select_connection_form": select_connection_form}
                    return render(request, SELECT_DATASET_CONNECTION_TEMPLATE_NAME, context)

        elif request.POST["Operation"] == "Save":
            connection = Connection.objects.get(pk=request.POST["connection"])
            if connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
                dataset_form = AddAzureBlobStorageDatasetForm(data=request.POST)
                saved = save_azure_blob_storage_data(dataset_form)
            else:
                add_dataset_form = get_add_dataset_form(request.POST)
                dataset_form = find_appropriate_dataset_form(add_dataset_form, request.POST)
                saved = save_dataset(dataset_form)
            if saved:
                messages.success(request, MSG_SUCCESS_DATASET_CREATE)
                return redirect("saef_dataset")
            else:
                messages.error(request, MSG_ERROR_DATASET_FORM_INVALID)
                context = {"add_dataset_form": AddDatasetForm([], data=request.POST)}
                return render(request, ADD_DATASET_TEMPLATE_NAME, context)

    else:
        select_connection_form = SelectConnectionForm()

    context = {"select_connection_form": select_connection_form}
    return render(request, SELECT_DATASET_CONNECTION_TEMPLATE_NAME, context)
