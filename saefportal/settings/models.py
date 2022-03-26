import pytz

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from solo.models import SingletonModel


class Contact(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=256)

    def __str__(self):
        return self.name


class Settings(SingletonModel):
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in pytz.common_timezones], default="UTC")

    datalake_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    datalake_id = models.PositiveIntegerField(blank=True, null=True)
    datalake = GenericForeignKey("datalake_type", "datalake_id")

    dataset_refresh_frequency = models.CharField(max_length=10, blank=True, null=True)
    delete_outdated_frequency = models.CharField(max_length=10, blank=True, null=True)
    # The threshold is specified in minutes.
    delete_outdated_threshold = models.PositiveIntegerField(blank=True, null=True)
    try_live_connection = models.BooleanField(default=False)

    profile_expected_datasets_n = models.IntegerField(default=10)
    profile_failed_threshold = models.FloatField(default=0.5)
    profile_delta_deviation = models.FloatField(default=0.2)

    email_host_user = models.CharField(max_length=100, default="")
    email_host_password = models.CharField(max_length=100, default="")
    email_host = models.CharField(max_length=50, default="localhost")
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)

    class Meta:
        verbose_name = "settings"
