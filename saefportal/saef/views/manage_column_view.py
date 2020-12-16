from analyzer.recordset.recordset_factory import recordset_factory
from ..models import Dataset, DatasetMetadataColumn
from ..util import index_exist, is_null
from ..enums import ExtractionSchemeValues, ExtractionSchemeNames, ConnectionType

from saefportal.settings import MSG_SUCCESS_DATA_SAVE, MSG_SUCCESS_EXTRACT_UNSAVED

from django.shortcuts import get_object_or_404, redirect, render
from django.forms.models import inlineformset_factory, modelform_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required()
def manage_column(request, dataset_id):
    ColumnForm = modelform_factory(DatasetMetadataColumn, fields=('dataset', 'column_name', 'data_type', 'is_null'))
    ColumnFormSet = inlineformset_factory(Dataset, DatasetMetadataColumn,
                                          form=ColumnForm, extra=0, can_delete=True)
    ColumnFormSetAdd = inlineformset_factory(Dataset, DatasetMetadataColumn,
                                             form=ColumnForm, extra=1, can_delete=False)
    dataset = get_object_or_404(Dataset, id=dataset_id)
    dataset_is_azure_blob_storage = True if \
        dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value else False
    saved = False
    if request.method == "POST":
        if request.POST["Operation"] == "Save":
            if request.POST.get('Extraction') == 'true':
                formset = ColumnFormSet(instance=dataset)
                # Deleting all columns as they are replaced with extraction
                for form in formset:
                    obj = form.save(commit=False)
                    obj.delete()

            formset = ColumnFormSet(request.POST, instance=dataset)

            if formset.is_valid():
                formset.save()
                saved = True
                messages.success(request, MSG_SUCCESS_DATA_SAVE)

        if request.POST["Operation"] == 'Add':
            formset = ColumnFormSetAdd(instance=dataset)
            context = {
                "formset": formset,
                "dataset": dataset,
                "saved": saved,
                "dataset_is_azure_blob_storage": dataset_is_azure_blob_storage
            }
            return render(request, 'manage_column/manage_column.html', context)

        if request.POST["Operation"] == 'Undo':
            return redirect('manage_column', dataset_id=dataset_id)

        if request.POST["Operation"] == 'Return':
            return redirect('dataset_detail', dataset_id=dataset_id)

        if request.POST["Operation"] == "Extract scheme":
            if dataset_is_azure_blob_storage:
                return extract_azure_blob_storage_schema(dataset, ColumnForm, ColumnFormSet, request, saved,
                                                         dataset_is_azure_blob_storage)
            else:
                return extract_schema(dataset, ColumnForm, ColumnFormSet, request, saved)

    formset = ColumnFormSet(instance=dataset)
    context = {
        "formset": formset,
        "dataset": dataset,
        "saved": saved,
        "dataset_is_azure_blob_storage": dataset_is_azure_blob_storage
    }
    return render(request, 'manage_column/manage_column.html', context)


def extract_azure_blob_storage_schema(dataset, ColumnForm, ColumnFormSet, request, saved,
                                      dataset_is_azure_blob_storage):
    recordset = recordset_factory(dataset)
    data_type_list = recordset.extract_schema(None, None)

    if not data_type_list:
        formset = ColumnFormSet(instance=dataset)
        context = {
            "formset": formset,
            "dataset": dataset,
            "saved": saved,
            "dataset_is_azure_blob_storage": dataset_is_azure_blob_storage
        }
        return render(request, 'manage_column/manage_column.html', context)

    ColumnFormSetExtract = inlineformset_factory(Dataset,
                                                 DatasetMetadataColumn,
                                                 form=ColumnForm,
                                                 extra=len(data_type_list),
                                                 can_delete=False)
    formset = ColumnFormSet(instance=dataset)

    # Verifying differences of columns
    difference_columns_dict = {}
    deleted_columns_dict = {}

    for index in range(0, len(data_type_list)):
        difference_columns_dict[index] = {}
        add_difference(difference_columns_dict, 'add', index)

    for index, form in enumerate(formset):
        difference_columns_dict[index] = {}
        obj = form.save(commit=False)

        add_difference(difference_columns_dict, 'nothing', index)

        # If dataset contains changes compared to the result from the database
        if index_exist(index, data_type_list):
            if obj.column_name != data_type_list[index][ExtractionSchemeValues.COLUMNNAME.value]:
                difference_columns_dict[index][ExtractionSchemeNames.COLUMNNAME.value] = {'status': 'changes'}
            if obj.data_type != data_type_list[index][ExtractionSchemeValues.DATATYPE.value]:
                difference_columns_dict[index][ExtractionSchemeNames.DATATYPE.value] = {'status': 'changes'}
        # If the dataset has more rows then the result from the database
        else:
            deleted_columns_dict[index] = {}
            deleted_columns_dict[index][ExtractionSchemeNames.COLUMNNAME.value] = obj.column_name
            deleted_columns_dict[index][ExtractionSchemeNames.DATATYPE.value] = obj.data_type
            deleted_columns_dict[index][ExtractionSchemeNames.ISNULL.value] = obj.is_null

    # Populating the initial data from the extracted scheme
    initial = []
    for data in data_type_list:
        initial.append({'dataset': dataset.pk,
                        'column_name': data[ExtractionSchemeValues.COLUMNNAME.value],
                        'data_type': data[ExtractionSchemeValues.DATATYPE.value],
                        'is_null': True})

    formset = ColumnFormSetExtract(queryset=DatasetMetadataColumn.objects.none(), initial=initial)
    messages.success(request, MSG_SUCCESS_EXTRACT_UNSAVED)

    context = {
        "formset": formset,
        "dataset": dataset,
        "saved": saved,
        "dataset_is_azure_blob_storage": dataset_is_azure_blob_storage,
        "difference": difference_columns_dict,
        "deleted": deleted_columns_dict,
        "extraction": True
    }

    return render(request, 'manage_column/manage_column.html', context)


def extract_schema(dataset, ColumnForm, ColumnFormSet, request, saved):
    # Retrieving the columnname, datatype and is null from the dataset
    recordset = recordset_factory(dataset)
    schema, table = dataset.dataset_extraction_table.split(".")
    result = recordset.extract_schema(schema, table)

    if not result:
        formset = ColumnFormSet(instance=dataset)
        return render(request, 'manage_column/manage_column.html',
                      {'formset': formset, 'dataset': dataset, 'saved': saved})

    ColumnFormSeExtract = inlineformset_factory(Dataset, DatasetMetadataColumn,
                                                form=ColumnForm, extra=len(result), can_delete=False)
    formset = ColumnFormSet(instance=dataset)

    # Verifying differences of columns
    difference_columns_dict = {}
    deleted_columns_dict = {}

    for index in range(0, len(result)):
        difference_columns_dict[index] = {}
        add_difference(difference_columns_dict, 'add', index)

    for index, form in enumerate(formset):
        difference_columns_dict[index] = {}
        obj = form.save(commit=False)

        add_difference(difference_columns_dict, 'nothing', index)

        # If dataset contains changes compared to the result from the database
        if index_exist(index, result):
            if obj.column_name != result[index][ExtractionSchemeValues.COLUMNNAME.value]:
                difference_columns_dict[index][ExtractionSchemeNames.COLUMNNAME.value] = {'status': 'changes'}
            if obj.data_type != result[index][ExtractionSchemeValues.DATATYPE.value]:
                difference_columns_dict[index][ExtractionSchemeNames.DATATYPE.value] = {'status': 'changes'}
            if obj.is_null != is_null(result[index][ExtractionSchemeValues.ISNULL.value]):
                difference_columns_dict[index][ExtractionSchemeNames.ISNULL.value] = {'status': 'changes'}
        # If the dataset has more rows then the result from the database
        else:
            deleted_columns_dict[index] = {}
            deleted_columns_dict[index][ExtractionSchemeNames.COLUMNNAME.value] = obj.column_name
            deleted_columns_dict[index][ExtractionSchemeNames.DATATYPE.value] = obj.data_type
            deleted_columns_dict[index][ExtractionSchemeNames.ISNULL.value] = obj.is_null

    # Populating the initial data from the extracted scheme
    initial = []
    for data in result:
        initial.append({'dataset': dataset.pk,
                        'column_name': data[ExtractionSchemeValues.COLUMNNAME.value],
                        'data_type': data[ExtractionSchemeValues.DATATYPE.value],
                        'is_null': is_null(data[ExtractionSchemeValues.ISNULL.value])})

    formset = ColumnFormSeExtract(queryset=DatasetMetadataColumn.objects.none(), initial=initial)
    messages.success(request, MSG_SUCCESS_EXTRACT_UNSAVED)

    return render(request, 'manage_column/manage_column.html',
                  {'formset': formset, 'dataset': dataset, 'saved': saved,
                   'difference': difference_columns_dict, 'deleted': deleted_columns_dict, 'extraction': True})


def add_difference(difference_columns_dict, status, index):
    difference_columns_dict[index]['Column name'] = {'status': status}
    difference_columns_dict[index]['Data type'] = {'status': status}
    difference_columns_dict[index]['Is null'] = {'status': status}
