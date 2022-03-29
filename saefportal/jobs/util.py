import json
from datetime import datetime

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from jobs import models
from jobs.forms.template_task_forms import TaskForm, RefreshDataTaskForm


def get_task_form(task):
    """Return form that can be used to run the given task."""
    if task == models.Job.TemplateTask.PROFILE_DATASET or task == models.Job.TemplateTask.EXTRACT_METADATA:
        return TaskForm
    elif task == models.Job.TemplateTask.REFRESH_DATA:
        return RefreshDataTaskForm


def clear_alert_fields(job, request):
    """Clear alert fields if checkbox to include them is not checked."""
    if "alert-checkbox" not in request.POST:
        job.alert_on_start_email = None
        job.alert_on_success_email = None
        job.alert_on_failure_email = None


def modify_periodic_tasks(job, request):
    """Create, delete or update an object in the periodic tasks using the schedule settings of the given job."""
    # If the job is made manual, delete the connected periodic task.
    if PeriodicTask.objects.filter(name=job.id).exists() and "schedule-checkbox" not in request.POST:
        PeriodicTask.objects.get(name=job.id).delete()
    else:
        cron_syntax = request.POST["cron-input"].split(" ")
        schedule, _ = CrontabSchedule.objects.get_or_create(minute=cron_syntax[0],
                                                            hour=cron_syntax[1],
                                                            day_of_week=cron_syntax[4],
                                                            day_of_month=cron_syntax[2],
                                                            month_of_year=cron_syntax[3])

        keyword_args = {"job_id": job.id, "user": request.user.email, "task_parameters": get_job_parameters(request)}
        start_datetime = datetime.strptime(request.POST["schedule_start_time"], "%Y-%m-%d %H:%M")

        # If the job is created or made scheduled, create an equivalent periodic task.
        if not PeriodicTask.objects.filter(name=job.id).exists() and "schedule-checkbox" in request.POST:
            PeriodicTask.objects.create(name=job.id, task="analyzer.tasks.tasks.run_job_task", crontab=schedule,
                                        kwargs=json.dumps(keyword_args), start_time=start_datetime)
        # If not, save the potentially changed schedule settings to the existing periodic task.
        else:
            PeriodicTask.objects.filter(name=job.id).update(crontab=schedule, kwargs=json.dumps(keyword_args),
                                                            start_time=start_datetime)


def get_job_parameters(request):
    """Set the parameters of the job using the custom form if using a template task."""
    # Custom template task form fields to check for.
    template_parameter_fields = ["dataset_key", "degree_of_change_threshold"]

    return {field: request.POST[field] for field in template_parameter_fields if field in request.POST}
