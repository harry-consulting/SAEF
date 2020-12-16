""" create models analyzers """
from __future__ import absolute_import, unicode_literals

from .enums import AnalyzerTask
from django.db import models
from saef.models import Application, Job, Dataset, DatasetSession
from django.contrib.postgres.fields import ArrayField


class AnalyzeSession(models.Model):
    analyzer_type = models.CharField(max_length=32, choices=AnalyzerTask.choices(),
                                     default=AnalyzerTask.ANALYZE_DATASET)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True)
    create_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('create_timestamp',)

    def __str__(self):
        return str(self.analyzer_type) + '_' + str(self.pk)


class ActualDatasetProfile(models.Model):
    dataset_session = models.ForeignKey(DatasetSession, on_delete=models.CASCADE, null=True)
    row_count = models.IntegerField()
    column_count = models.IntegerField()
    hash_sum = models.IntegerField(blank=True, null=True)


class ActualColumnProfile(models.Model):
    dataset_profile = models.ForeignKey(ActualDatasetProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    min = models.CharField(max_length=128, blank=True, null=True)
    max = models.CharField(max_length=128, blank=True, null=True)
    uniqueness = models.FloatField()
    datatype = models.CharField(max_length=128)
    nullable = models.BooleanField()
    order = models.IntegerField()
    hash_sum = models.IntegerField(blank=True, null=True)


class ExpectedDatasetProfile(models.Model):
    actual_dataset_profile = models.ForeignKey(ActualDatasetProfile, on_delete=models.CASCADE, null=True)
    row_count = models.FloatField()
    column_count = models.FloatField()
    hash_sum = models.FloatField(blank=True, null=True)


class ExpectedColumnProfile(models.Model):
    dataset_profile = models.ForeignKey(ExpectedDatasetProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    min = models.CharField(max_length=128, blank=True, null=True)
    max = models.CharField(max_length=128, blank=True, null=True)
    uniqueness = models.FloatField()
    datatype = models.CharField(max_length=128)
    nullable = models.BooleanField()
    order = models.IntegerField()
    hash_sum = models.FloatField(blank=True, null=True)


class RatioCount(models.Model):
    dataset_ratio = models.ForeignKey(ActualDatasetProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    actual = models.FloatField()
    expected = models.FloatField()
    ratio = models.FloatField()


class RatioColumn(models.Model):
    dataset_ratio = models.ForeignKey(ActualDatasetProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    changes = models.BooleanField()
    columns = ArrayField(models.CharField(max_length=128))
    ratio = models.FloatField()
