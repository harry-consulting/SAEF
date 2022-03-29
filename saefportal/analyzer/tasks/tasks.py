from django.utils import timezone

from analyzer.celery import app
from analyzer.tasks.task_delete_outdated_datalake_files import task_delete_outdated_datalake_files
from analyzer.tasks.task_extract_metadata import task_extract_metadata
from analyzer.tasks.task_profile_dataset import task_profile_dataset
from analyzer.tasks.task_refresh_all_datasets import task_refresh_all_datasets
from analyzer.tasks.task_refresh_data import task_refresh_data
from analyzer.tasks.util import send_run_email
from datasets.models import Dataset, DatasetRun
from jobs.models import JobRun, Job


@app.task
def run_job_task(job_id, user, task_parameters):
    """Run the job with the given arguments and create both a dataset run and job run for the task execution."""
    job = Job.objects.get(id=job_id)
    job_run = JobRun.objects.create(job=job, parameters=task_parameters)
    send_run_email("start", job)

    task_result = run_task(job.get_task()[2], user, task_parameters, run_type=DatasetRun.Type.JOB)

    send_run_email("failure", job) if "error" in task_result["result"] else send_run_email("success", job)

    # Update the job run object with the final state of the task.
    job_run.result = task_result["result"]
    job_run.status = task_result["status"]
    job_run.end_datetime = task_result["end_datetime"]

    job_run.save()


@app.task
def run_task(task_name, user, task_parameters, run_type=DatasetRun.Type.API):
    """Run the given task and return a dict containing the result, status and end datetime."""
    dataset = Dataset.objects.get(key=task_parameters["dataset_key"])
    dataset_run = DatasetRun.objects.create(dataset=dataset, task_name=task_name, created_by=user, type=run_type)

    task_fun = task_dict[task_name]
    result = task_fun(dataset_run=dataset_run, task_parameters=task_parameters)

    dataset_run.result = result
    dataset_run.end_datetime = timezone.now()

    if "error" in result:
        dataset_run.status = DatasetRun.Status.FAILED

    dataset_run.save()

    return {"result": result, "status": dataset_run.status, "end_datetime": dataset_run.end_datetime}


@app.task
def refresh_all_datasets():
    task_refresh_all_datasets()


@app.task
def delete_outdated_datalake_files(threshold_minutes):
    task_delete_outdated_datalake_files(threshold_minutes)


@app.task
def ping():
    return "pong"


task_dict = {
    Job.TemplateTask.PROFILE_DATASET.label: task_profile_dataset,
    Job.TemplateTask.EXTRACT_METADATA.label: task_extract_metadata,
    Job.TemplateTask.REFRESH_DATA.label: task_refresh_data
}
