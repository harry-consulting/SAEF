from bootstrap_modal_forms.forms import BSModalForm
from django import forms
from django.template.defaultfilters import mark_safe


class TaskForm(BSModalForm):
    dataset_key = forms.CharField(label="Dataset key", max_length=100, required=False,
                                  widget=forms.TextInput(attrs={"placeholder": "Dataset key"}))


class RefreshDataTaskForm(TaskForm):
    degree_of_change_threshold = forms.FloatField(label=mark_safe("Degree of change threshold - <i>Optional</i>"),
                                                  min_value=0, max_value=1, required=False,
                                                  widget=forms.NumberInput(attrs={
                                                      "step": "0.05", "info": "If the degree of change is below this "
                                                                              "threshold, the data is not refreshed."
                                                  }))
