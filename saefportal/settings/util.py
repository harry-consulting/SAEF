import json

from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from util.dropbox_util import start_dropbox_authentication
from util.google_util import start_google_authentication
from util.one_drive_util import start_one_drive_authentication
from datalakes.models import AzureBlobStorageDatalake, AzureDataLakeDatalake, AmazonS3Datalake, LocalDatalake
from datalakes.util import initialize_datalake
from settings.models import Settings


def send_email_using_settings(subject, message, recipient_list):
    """Send an email using the SAEF email server settings."""
    settings = Settings.objects.get()

    # Use the email information in the SAEF settings, if specified.
    if settings.email_host_user:
        email_backend = EmailBackend(host=settings.email_host, port=settings.email_port, use_tls=settings.email_use_tls,
                                     username=settings.email_host_user, password=settings.email_host_password)

        send_mail(subject=subject, message=message, from_email=settings.email_host_user, recipient_list=recipient_list,
                  auth_user=settings.email_host_user, auth_password=settings.email_host_password,
                  connection=email_backend)
    # If not specified in the SAEF settings, use the default email information from the django settings.
    else:
        send_mail(subject=subject, message=message, from_email=settings.email_host_user, recipient_list=recipient_list)


def get_or_create_crontab_schedule(cron_syntax):
    schedule, _ = CrontabSchedule.objects.get_or_create(minute=cron_syntax[0],
                                                        hour=cron_syntax[1],
                                                        day_of_week=cron_syntax[4],
                                                        day_of_month=cron_syntax[2],
                                                        month_of_year=cron_syntax[3])

    return schedule


def modify_refresh_all_task(settings, request):
    """Modify the related periodic task based on the new state of the dataset refresh frequency setting."""
    task_name = "refresh all datasets"

    if "refresh-checkbox" not in request.POST:
        settings.dataset_refresh_frequency = None
        PeriodicTask.objects.filter(name=task_name).delete()
    else:
        cron_syntax = request.POST["dataset_refresh_frequency"].split(" ")
        schedule = get_or_create_crontab_schedule(cron_syntax)

        if PeriodicTask.objects.filter(name=task_name).exists():
            PeriodicTask.objects.filter(name=task_name).update(crontab=schedule)
        else:
            PeriodicTask.objects.create(name=task_name, crontab=schedule,
                                        task="analyzer.tasks.tasks.refresh_all_datasets")


def modify_delete_outdated_task(settings, request):
    """Modify the related periodic task based on the new state of the "delete outdated" settings."""
    task_name = "delete outdated snapshots"

    if "delete-outdated-checkbox" not in request.POST:
        settings.delete_outdated_frequency = None
        settings.delete_outdated_threshold = None

        PeriodicTask.objects.filter(name=task_name).delete()
    else:
        cron_syntax = request.POST["delete_outdated_frequency"].split(" ")
        schedule = get_or_create_crontab_schedule(cron_syntax)

        keyword_args = {"threshold_minutes": int(request.POST["delete_outdated_threshold"])}

        if PeriodicTask.objects.filter(name=task_name).exists():
            PeriodicTask.objects.filter(name=task_name).update(crontab=schedule, kwargs=json.dumps(keyword_args))
        else:
            PeriodicTask.objects.create(name=task_name, crontab=schedule, kwargs=json.dumps(keyword_args),
                                        task="analyzer.tasks.tasks.delete_outdated_datalake_files")


def group_datalake_types():
    """Return the possible datalake types, grouped into the categories "File-based" and "BLOB-based"."""

    class Type(models.TextChoices):
        AMAZON_S3 = "AMAZON_S3", _("Amazon S3")
        AZURE_BLOB_STORAGE = "AZURE_BLOB_STORAGE", _("Azure Blob Storage")
        AZURE_DATA_LAKE = "AZURE_DATA_LAKE", _("Azure Data Lake")
        DROPBOX = "DROPBOX", _("Dropbox")
        GOOGLE_CLOUD_STORAGE = "GOOGLE_CLOUD_STORAGE", _("Google Cloud Storage")
        GOOGLE_DRIVE = "GOOGLE_DRIVE", _("Google Drive")
        LOCAL = "LOCAL", _("Local")
        ONEDRIVE = "ONEDRIVE", _("OneDrive")

    return {"File-based": [Type.DROPBOX, Type.GOOGLE_DRIVE, Type.LOCAL, Type.ONEDRIVE],
            "BLOB-based": [Type.AZURE_BLOB_STORAGE, Type.AZURE_DATA_LAKE, Type.AMAZON_S3, Type.GOOGLE_CLOUD_STORAGE]}


def connect_to_datalake(request, form):
    datalake = None

    if form.data["type"] == "ONEDRIVE":
        return start_one_drive_authentication(request, form, "datalake")
    elif form.data["type"] == "GOOGLE_DRIVE":
        return start_google_authentication(request, form, "datalake")
    elif form.data["type"] == "GOOGLE_CLOUD_STORAGE":
        return start_google_authentication(request, form, "datalake")
    elif form.data["type"] == "DROPBOX":
        return start_dropbox_authentication(request, form, "datalake")
    elif form.data["type"] == "AZURE_BLOB_STORAGE":
        datalake = AzureBlobStorageDatalake.objects.create(connection_string=form.data["connection_string"],
                                                           container_name=form.data["blob_container"])
    elif form.data["type"] == "AZURE_DATA_LAKE":
        datalake = AzureDataLakeDatalake.objects.create(connection_string=form.data["connection_string"],
                                                        container_name=form.data["blob_container"])
    elif form.data["type"] == "AMAZON_S3":
        datalake = AmazonS3Datalake.objects.create(access_key_id=form.data["access_key_id"],
                                                   secret_access_key=form.data["secret_access_key"],
                                                   bucket_name=form.data["bucket_name"])
    elif form.data["type"] == "LOCAL":
        datalake = LocalDatalake.objects.create(root_path=form.data["root_path"])

    if datalake:
        initialize_datalake(datalake, request, "migrate-checkbox" in request.POST)

    return HttpResponseRedirect(reverse_lazy("settings:settings", args=[1]))
