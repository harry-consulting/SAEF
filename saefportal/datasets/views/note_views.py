from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from datasets.models import Dataset, Note


@login_required
def create_note(request):
    dataset_id = request.POST.get("dataset_id", None)
    note_text = request.POST.get("note_text", None)

    # Only create the note if the requesting user has at least view permission for the dataset.
    if request.user.has_permission("view_dataset", Dataset.objects.get(id=dataset_id)):
        Note.objects.create(dataset_id=dataset_id, text=note_text, created_by_id=request.user.id)

    return render_modified_note_content(request, dataset_id)


@login_required
@csrf_exempt
def delete_note(request, dataset_id, note_id):
    # Only delete the note if the requesting user has at least view permission for the dataset.
    if request.user.has_permission("view_dataset", Dataset.objects.get(id=dataset_id)):
        Note.objects.filter(id=note_id).delete()

    return render_modified_note_content(request, dataset_id)


def render_modified_note_content(request, dataset_id):
    """Helper function to return modified content in note modification views."""
    dataset = Dataset.objects.get(id=dataset_id)

    # Adding "ajax": True to the context to avoid collapsing the note card when modifying notes through ajax requests.
    return render(request, "datasets/dataset_detail/notes.html", {"dataset": dataset, "ajax": True})
