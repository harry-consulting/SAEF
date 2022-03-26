from django.db import models


class ActualDatasetProfile(models.Model):
    dataset_run = models.ForeignKey("datasets.DatasetRun", on_delete=models.CASCADE, null=True)
    row_count = models.IntegerField()
    column_count = models.IntegerField()
    hash_sum = models.IntegerField(blank=True, null=True)


class ActualColumnProfile(models.Model):
    dataset_profile = models.ForeignKey(ActualDatasetProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    min = models.CharField(max_length=128, blank=True, null=True)
    max = models.CharField(max_length=128, blank=True, null=True)
    uniqueness = models.FloatField(blank=True, null=True)
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
    uniqueness = models.FloatField(blank=True, null=True)
    datatype = models.CharField(max_length=128)
    nullable = models.BooleanField()
    order = models.IntegerField()
    hash_sum = models.FloatField(blank=True, null=True)
