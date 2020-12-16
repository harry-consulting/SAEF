from analyzer.recordset.recordset_factory import recordset_factory
from django.urls import reverse

from ..models import Dataset, DatasetMetadataConstraint, PostgresConnection

from django.forms.models import inlineformset_factory, modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required()
def manage_constraint(request, dataset_id):
    ConstraintForm = modelform_factory(DatasetMetadataConstraint, fields=(
        'dataset', 'constraint_name', 'columns', 'constraint_type', 'constraint_definition'))
    ConstraintFormSet = inlineformset_factory(Dataset, DatasetMetadataConstraint,
                                              form=ConstraintForm, extra=0, can_delete=True)
    ConstraintFormSetAdd = inlineformset_factory(Dataset, DatasetMetadataConstraint,
                                                 form=ConstraintForm, extra=1, can_delete=False)
    dataset = get_object_or_404(Dataset, id=dataset_id)
    if request.method == "POST":
        if request.POST["Operation"] == "Save":
            if request.POST.get('Extraction') == 'true':
                formset = ConstraintFormSet(instance=dataset)
                for form in formset:
                    obj = form.save(commit=False)
                    obj.delete()

            formset = ConstraintFormSet(request.POST, instance=dataset)

            if formset.is_valid():
                formset.save()
                messages.success(request, 'Data was saved successfully.')
                return render(request, "manage_constraint/manage_constraint.html", {"formset": formset, "dataset": dataset})

        if request.POST["Operation"] == 'Add':
            formset = ConstraintFormSetAdd(instance=dataset)
            return render(request, 'manage_constraint/manage_constraint.html', {'formset': formset, 'dataset': dataset})

        if request.POST["Operation"] == 'Return':
            return redirect("dataset_detail", dataset_id=dataset_id)

        if request.POST["Operation"] == "Undo":
            return redirect(reverse("manage_constraint", kwargs={"dataset_id": dataset_id}))

        if request.POST["Operation"] == "Extract":
            recordset = recordset_factory(dataset)
            access_method = dataset.dataset_access_method

            if access_method == 'TABLE':
                table = dataset.dataset_extraction_table.split(".")[1]

                pk_and_unique_constraints = recordset.get_pk_and_unique_constraints(table)
                check_constraints = recordset.get_check_constraints(table)
                is_nullable_constraints = recordset.get_is_nullable_constraints(table)

                form = []
                form = fill_constraint_form(pk_and_unique_constraints, form, dataset, kind="PRIMARY KEY")
                form = fill_constraint_form(check_constraints, form, dataset, kind="CHECK")
                form = fill_constraint_form(is_nullable_constraints, form, dataset, kind="IS_NULLABLE")

                ConstraintFormSetExtract = inlineformset_factory(Dataset, DatasetMetadataConstraint,
                                                                 form=ConstraintForm, extra=len(form),
                                                                 can_delete=False)

                formset = ConstraintFormSetExtract(queryset=DatasetMetadataConstraint.objects.none(), initial=form)
                return render(request, 'manage_constraint/manage_constraint.html', {'formset': formset, 'dataset': dataset, "extraction": True})

    formset = ConstraintFormSet(instance=dataset)
    return render(request, 'manage_constraint/manage_constraint.html', {'formset': formset, 'dataset': dataset})


def fill_constraint_form(constraint, form, dataset, **kwargs):
    if kwargs["kind"] == "PRIMARY KEY":
        for i in range(len(constraint)):
            form.append({
                "dataset": dataset.pk,
                "constraint_name": constraint[i][0],
                "columns": constraint[i][1],
                "constraint_type": constraint[i][2],
                "constraint_definition": "{0} is primary key".format(constraint[i][1])
            })
        return form
    elif kwargs["kind"] == "CHECK":
        for i in range(len(constraint)):
            form.append({
                "dataset": dataset.pk,
                "constraint_name": constraint[i][0],
                "columns": constraint[i][1],
                "constraint_type": "CHECK",
                "constraint_definition": constraint[i][2]
            })
        return form
    elif kwargs["kind"] == "IS_NULLABLE":
        for i in range(len(constraint)):
            if constraint[i][1] == "NO":
                form.append({
                    "dataset": dataset.pk,
                    "constraint_name": "{0}_not_null".format(constraint[i][0]),
                    "columns": constraint[i][0],
                    "constraint_type": "IS_NULLABLE",
                    "constraint_definition": "{0} is not null".format(constraint[i][0])
                })
        return form
